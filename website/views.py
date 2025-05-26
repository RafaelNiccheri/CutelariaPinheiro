# website/views.py

import re
import json
from datetime import date, datetime
from flask import (Blueprint, render_template, request,redirect, url_for, flash, jsonify)
from flask_login import login_required, current_user
from sqlalchemy import func
from . import db
from .models import (Note,MateriaPrima,ProdutoAcabado,PedidoVenda,OrdemServico,ReposicaoMateriaPrima, ProductImage, Inventario, VendaNormal)
from werkzeug.utils import secure_filename
from . import allowed_file
from flask import current_app
import os
from datetime import datetime

views = Blueprint('views', __name__)


# ── Home / Notes ────────────────────────────────────────────────
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note_text = request.form.get('note')
        if not note_text or len(note_text) < 1:
            flash('Nota muito curta!', 'error')
        else:
            new_note = Note(data=note_text, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Nota adicionada!', 'success')

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', user=current_user, notes=notes)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    note = Note.query.get(data.get('noteId'))
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({}), 200


# ── Dashboard de Gestão ───────────────────────────────────────────
@views.route('/gestao')
@login_required
def gestao():
    # — filtro opcional de cliente para Pedidos/Vendas —
    search_cliente = request.args.get('cliente', '').strip()

    # — controla aba ativa —
    if search_cliente:
        active_tab = 'pv'
    else:
        active_tab = request.args.get('tab', 'mp')

    # — dados principais —
    materias   = MateriaPrima.query.all()
    produtos   = ProdutoAcabado.query.all()
    reposicoes = ReposicaoMateriaPrima.query.all()
    inventario = Inventario.query.all()
    vendas_normais = VendaNormal.query.all()
    ordens     = OrdemServico.query.all()

    # — Pedidos/Vendas, com busca por cliente se fornecido —
    if search_cliente:
        pedidos = PedidoVenda.query.filter(
            PedidoVenda.nome_cliente.ilike(f'%{search_cliente}%')
        ).all()
    else:
        pedidos = PedidoVenda.query.all()

    # — Itens abaixo do ponto de reposição —
    itens_baixo_estoque = MateriaPrima.query \
        .filter(MateriaPrima.quantidade_estoque < MateriaPrima.ponto_reposicao) \
        .all()

    # — Pedidos vencidos (não entregues) —
    pedidos_vencidos = PedidoVenda.query\
        .filter(
            PedidoVenda.data_prevista_entrega < date.today(),
            PedidoVenda.status != 'entregue'
        ).all()

    # — Produções em atraso: previsão passou e status ≠ 'concluída' —
    producoes_atrasadas = OrdemServico.query\
        .filter(
            OrdemServico.data_prevista_conclusao < date.today(),
            OrdemServico.status != 'concluída'
        ).all()

    # — Total de pedidos em andamento —
    total_pedidos_andamento = PedidoVenda.query\
        .filter(PedidoVenda.status.in_(
            ['recebido', 'produção', 'pronto', 'enviado']
        )).count()

    # — Soma das vendas do mês atual —
    vendas_pedidos_mes = db.session.query(
        func.coalesce(func.sum(PedidoVenda.valor_pedido), 0)
    ).filter(
        func.extract('year', PedidoVenda.data_pedido)  == datetime.now().year,
        func.extract('month', PedidoVenda.data_pedido) == datetime.now().month
    ).scalar()

    # — Soma das vendas normais do mês atual —
    vendas_normais_mes = db.session.query(
        func.coalesce(func.sum(VendaNormal.valor_venda), 0)
    ).filter(
        func.extract('year', VendaNormal.data_venda) == datetime.now().year,
        func.extract('month', VendaNormal.data_venda) == datetime.now().month
    ).scalar()

    # — Vendas do mês (pedidos + vendas normais) —
    vendas_mes = vendas_pedidos_mes + vendas_normais_mes

    return render_template(
        'gestao.html',
        user=current_user,
        materias=materias,
        produtos=produtos,
        pedidos=pedidos,
        ordens=ordens,
        reposicoes=reposicoes,
        itens_baixo_estoque=itens_baixo_estoque,
        pedidos_vencidos=pedidos_vencidos,
        producoes_atrasadas=producoes_atrasadas,
        total_pedidos_andamento=total_pedidos_andamento,
        vendas_mes=vendas_mes,
        search_cliente=search_cliente,
        inventario=inventario,
        vendas_normais=vendas_normais,
        active_tab=active_tab
    )



# ── Formulários “+ Novo” ───────────────────────────────────────────
@views.route('/gestao/mp/novo', methods=['GET', 'POST'])
@login_required
def nova_materia_prima():
    if request.method == 'POST':
        m = MateriaPrima(
            codigo_item=request.form['codigo_item'],
            tipo_material=request.form['tipo_material'],
            unidade=request.form['unidade'],
            quantidade_estoque=float(request.form['quantidade_estoque']),
            ponto_reposicao=float(request.form['ponto_reposicao']),
            fornecedor=request.form.get('fornecedor'),
            data_ultima_entrada=date.fromisoformat(request.form['data_ultima_entrada']),
            observacoes=request.form.get('observacoes')
        )
        db.session.add(m)
        db.session.commit()
        flash('Matéria-prima cadastrada!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('nova_materia_prima.html', user=current_user)


@views.route('/gestao/pa/novo', methods=['GET', 'POST'])
@login_required
def novo_produto_acabado():
    if request.method == 'POST':
        p = ProdutoAcabado(
            codigo_faca=request.form['codigo_faca'],
            tipo=request.form['tipo'],
            material_lamina=request.form['material_lamina'],
            material_cabo=request.form['material_cabo'],
            quantidade_disponivel=int(request.form['quantidade_disponivel']),
            quantidade_reservada=int(request.form['quantidade_reservada']),
            quantidade_vendida_mes=int(request.form['quantidade_vendida_mes']),
            observacoes=request.form.get('observacoes')
        )
        db.session.add(p)
        db.session.commit()
        flash('Produto acabado cadastrado!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('novo_produto_acabado.html', user=current_user)


# ── Novo Pedido/Venda ────────────────────────────────────────────
@views.route('/gestao/pv/novo', methods=['GET','POST'])
@login_required
def novo_pedido_venda():
    produtos = ProdutoAcabado.query.all()
    if request.method == 'POST':
        numero_pedido          = request.form['numero_pedido']
        nome_cliente           = request.form['nome_cliente']    # ← capturar
        produto_id             = int(request.form['produto_id'])
        quantidade             = int(request.form['quantidade'])
        personalizacao         = bool(request.form.get('personalizacao'))
        detalhes_personalizacao= request.form.get('detalhes_personalizacao')
        data_pedido            = date.fromisoformat(request.form['data_pedido'])
        status                 = request.form['status']
        data_prevista_entrega  = date.fromisoformat(request.form['data_prevista_entrega'])
        valor_pedido           = float(request.form['valor_pedido'])
        observacoes            = request.form.get('observacoes')

        solicitacao = f"{ProdutoAcabado.query.get(produto_id).codigo_faca} × {quantidade}"
        ped = PedidoVenda(
            numero_pedido           = numero_pedido,
            nome_cliente            = nome_cliente,
            produtos_solicitados    = solicitacao,
            personalizacao          = personalizacao,
            detalhes_personalizacao = detalhes_personalizacao,
            data_pedido             = data_pedido,
            status                  = status,
            data_prevista_entrega   = data_prevista_entrega,
            valor_pedido            = valor_pedido,
            observacoes             = observacoes
        )
        db.session.add(ped)
        db.session.commit()
        flash('Pedido/venda cadastrado!', 'success')
        return redirect(url_for('views.gestao'))

    return render_template(
        'novo_pedido_venda.html',
        user=current_user,
        produtos=produtos,
        date=date
    )

# ── Nova Ordem de Serviço ─────────────────────────────────────────
@views.route('/gestao/os/novo', methods=['GET','POST'])
@login_required
def nova_ordem_servico():
    produtos = ProdutoAcabado.query.all()

    if request.method == 'POST':
        # coleta o form
        numero_os               = request.form['numero_os']
        produto_id              = int(request.form['produto_id'])
        quantidade              = int(request.form['quantidade'])
        materiais_necessarios   = request.form['materiais_necessarios']
        data_inicio             = date.fromisoformat(request.form['data_inicio_producao'])
        data_prevista_conclusao = date.fromisoformat(request.form['data_prevista_conclusao'])
        responsavel             = request.form['responsavel']

        # criar sem 'vendido'
        os_ = OrdemServico(
            numero_os               = numero_os,
            produto_id              = produto_id,
            quantidade              = quantidade,
            materiais_necessarios   = materiais_necessarios,
            data_inicio_producao    = data_inicio,
            data_prevista_conclusao = data_prevista_conclusao,
            responsavel             = responsavel
            # status padrão já vem do model: 'produção'
        )
        db.session.add(os_)

        # consome matéria‐prima
        for code, qty in re.findall(r'(\w+)\s*[×x]\s*([\d\.]+)', materiais_necessarios):
            mat = MateriaPrima.query.filter_by(codigo_item=code).first()
            if mat:
                mat.quantidade_estoque = max(mat.quantidade_estoque - float(qty), 0)
                db.session.add(mat)

        db.session.commit()
        flash('Ordem de serviço criada em produção!', 'success')
        return redirect(url_for('views.gestao'))

    return render_template(
        'nova_ordem_servico.html',
        user=current_user,
        produtos=produtos,
        date=date
    )



@views.route('/gestao/reposicao/novo', methods=['GET', 'POST'])
@login_required
def nova_reposicao_materia_prima():
    if request.method == 'POST':
        status = request.form['status']
        rp = ReposicaoMateriaPrima(
            materia_id=int(request.form['materia_id']),
            quantidade_reposicao=float(request.form['quantidade_reposicao']),
            data_solicitacao=date.fromisoformat(request.form['data_solicitacao']),
            data_previsao_reposicao=date.fromisoformat(request.form['data_previsao_reposicao']),
            fornecedor=request.form.get('fornecedor'),
            status=status,
            observacoes=request.form.get('observacoes')
        )
        db.session.add(rp)

        # Só ajusta estoque se iniciar já como "recebido"
        if status == 'recebido':
            mat = MateriaPrima.query.get(rp.materia_id)
            if mat:
                mat.quantidade_estoque += rp.quantidade_reposicao
                db.session.add(mat)

        db.session.commit()
        flash(
            'Requisição de reposição cadastrada!'
            + (' Estoque atualizado.' if status == 'recebido' else ''),
            'success'
        )
        return redirect(url_for('views.gestao'))

    materias = MateriaPrima.query.all()
    return render_template('nova_reposicao.html',user=current_user,materias=materias,date=date)


@views.route('/gestao/reposicao/edit/<int:rp_id>', methods=['GET', 'POST'])
@login_required
def edit_reposicao_materia_prima(rp_id):
    rp = ReposicaoMateriaPrima.query.get_or_404(rp_id)
    old_status = rp.status

    if request.method == 'POST':
        new_status = request.form['status']
        rp.status = new_status

        mat = MateriaPrima.query.get(rp.materia_id)
        if mat:
            if old_status != 'recebido' and new_status == 'recebido':
                mat.quantidade_estoque += rp.quantidade_reposicao
            elif old_status == 'recebido' and new_status in ['solicitado', 'em trânsito']:
                mat.quantidade_estoque = max(mat.quantidade_estoque - rp.quantidade_reposicao, 0.0)
            db.session.add(mat)

        db.session.commit()
        flash(f'Status da reposição #{rp.id} atualizado para "{rp.status}" e estoque ajustado.', 'success')
        return redirect(url_for('views.gestao'))

    return render_template('edit_reposicao.html', user=current_user, reposicao=rp)


@views.route('/gestao/pv/edit/<int:ped_id>', methods=['GET', 'POST'])
@login_required
def edit_pedido_venda(ped_id):
    ped = PedidoVenda.query.get_or_404(ped_id)
    if request.method == 'POST':
        ped.status = request.form['status']
        db.session.commit()
        flash(f'Pedido #{ped.numero_pedido} atualizado para "{ped.status}"', 'success')
        return redirect(url_for('views.gestao'))

    return render_template(
        'edit_pedido_venda.html',
        user=current_user,
        pedido=ped
    )


# Listar + upload + delete + set primary
@views.route('/gestao/pa/<int:prod_id>/images', methods=['GET', 'POST'])
@login_required
def manage_product_images(prod_id):
    prod = ProdutoAcabado.query.get_or_404(prod_id)

    if request.method == 'POST' and 'file' in request.files:
        f = request.files['file']
        if f.filename and allowed_file(f.filename):
            filename = secure_filename(f"{prod_id}_{datetime.utcnow().timestamp()}_{f.filename}")
            dest = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            f.save(dest)
            img = ProductImage(product_id=prod_id, filename=filename)
            db.session.add(img)
            db.session.commit()
            flash('Imagem enviada!', 'success')
        else:
            flash('Formato inválido.', 'error')
        return redirect(url_for('views.manage_product_images', prod_id=prod_id))

    images = prod.images
    return render_template(
        'manage_images.html',
        user=current_user,
        produto=prod,
        images=images
    )



@views.route('/gestao/pa/<int:prod_id>/images/delete/<int:img_id>', methods=['POST'])
@login_required
def delete_product_image(prod_id, img_id):
    img = ProductImage.query.get_or_404(img_id)
    # remove arquivo
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
    if os.path.exists(path): os.remove(path)
    db.session.delete(img)
    db.session.commit()
    flash('Imagem removida.', 'success')
    return redirect(url_for('views.manage_product_images', prod_id=prod_id))


@views.route('/gestao/pa/<int:prod_id>/images/set_primary/<int:img_id>', methods=['POST'])
@login_required
def set_primary_image(prod_id, img_id):
    prod = ProdutoAcabado.query.get_or_404(prod_id)
    # limpa primárias
    for i in prod.images:
        i.is_primary = False
    img = ProductImage.query.get_or_404(img_id)
    img.is_primary = True
    db.session.commit()
    flash('Imagem principal atualizada.', 'success')
    return redirect(url_for('views.manage_product_images', prod_id=prod_id))


@views.route('/gestao/os/edit/<int:os_id>', methods=['GET','POST'])
@login_required
def edit_ordem_servico(os_id):
    os_         = OrdemServico.query.get_or_404(os_id)
    prev_status = os_.status

    if request.method == 'POST':
        new_status = request.form['status']
        os_.status = new_status

        # se passou para 'concluída'
        if prev_status != 'concluída' and new_status == 'concluída':
            # tenta achar inventário existente
            inv = Inventario.query.filter_by(produto_id=os_.produto_id).first()
            if inv:
                # soma a quantidade
                inv.quantidade += os_.quantidade
            else:
                # cria novo registro
                inv = Inventario(
                    produto_id = os_.produto_id,
                    quantidade = os_.quantidade
                )
                db.session.add(inv)
            # remove a OS concluída
            db.session.delete(os_)

        else:
            # qualquer outro status, só atualiza a OS
            db.session.add(os_)

        db.session.commit()
        flash(f'OS #{os_.numero_os} atualizada para "{new_status}".', 'success')
        return redirect(url_for('views.gestao'))

    return render_template('edit_ordem_servico.html',
                           user=current_user,
                           os=os_)

@views.route('/gestao/venda_normal/novo', methods=['GET','POST'])
@login_required
def nova_venda_normal():
    produtos = ProdutoAcabado.query.all()

    if request.method == 'POST':
        produto_id  = int(request.form['produto_id'])
        quantidade  = int(request.form['quantidade'])
        cliente     = request.form['cliente']
        valor_venda = float(request.form['valor_venda'])
        data_venda  = date.fromisoformat(request.form['data_venda'])

        # 1) busca o registro de inventário
        inv = Inventario.query.filter_by(produto_id=produto_id).first()

        # 2) valida estoque
        if not inv or inv.quantidade < quantidade:
            flash('Estoque insuficiente no inventário para essa venda.', 'error')
            return redirect(url_for('views.nova_venda_normal'))

        # 3) subtrai do inventário
        inv.quantidade -= quantidade
        db.session.add(inv)

        # 4) registra a venda
        venda = VendaNormal(
            produto_id  = produto_id,
            cliente     = cliente,
            quantidade  = quantidade,
            valor_venda = valor_venda,
            data_venda  = data_venda
        )
        db.session.add(venda)

        db.session.commit()
        flash('Venda registrada e inventário atualizado!', 'success')
        return redirect(url_for('views.gestao'))

    return render_template(
        'novo_venda_normal.html',
        produtos=produtos,
        date=date,
        user=current_user
    )