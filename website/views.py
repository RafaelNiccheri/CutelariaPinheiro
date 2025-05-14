# website/views.py

import re
import json
from datetime import date, datetime
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy import func

from . import db
from .models import (
    Note,
    MateriaPrima,
    ProdutoAcabado,
    PedidoVenda,
    OrdemServico,
    ReposicaoMateriaPrima
)

views = Blueprint('views', __name__)

<<<<<<< HEAD
=======

>>>>>>> e304e52 (commit ajuste flask)
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

<<<<<<< HEAD
=======

>>>>>>> e304e52 (commit ajuste flask)
@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    note = Note.query.get(data.get('noteId'))
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({}), 200

<<<<<<< HEAD
=======

>>>>>>> e304e52 (commit ajuste flask)
# ── Dashboard de Gestão ───────────────────────────────────────────
@views.route('/gestao')
@login_required
def gestao():
<<<<<<< HEAD
    materias   = MateriaPrima.query.all()
    produtos   = ProdutoAcabado.query.all()
    pedidos    = PedidoVenda.query.all()
    ordens     = OrdemServico.query.all()
=======
    materias = MateriaPrima.query.all()
    produtos = ProdutoAcabado.query.all()
    pedidos = PedidoVenda.query.all()
    ordens = OrdemServico.query.all()
>>>>>>> e304e52 (commit ajuste flask)
    reposicoes = ReposicaoMateriaPrima.query.all()

    itens_baixo_estoque = MateriaPrima.query \
        .filter(MateriaPrima.quantidade_estoque < MateriaPrima.ponto_reposicao) \
        .all()

    pedidos_vencidos = PedidoVenda.query \
        .filter(
<<<<<<< HEAD
            PedidoVenda.data_prevista_entrega < date.today(),
            PedidoVenda.status != 'entregue'
        ) \
=======
        PedidoVenda.data_prevista_entrega < date.today(),
        PedidoVenda.status != 'entregue'
    ) \
>>>>>>> e304e52 (commit ajuste flask)
        .all()

    producoes_atrasadas = OrdemServico.query \
        .filter(
<<<<<<< HEAD
            OrdemServico.data_prevista_conclusao < date.today(),
            OrdemServico.status != 'concluida'
        ) \
=======
        OrdemServico.data_prevista_conclusao < date.today(),
        OrdemServico.status != 'concluida'
    ) \
>>>>>>> e304e52 (commit ajuste flask)
        .all()

    total_pedidos_andamento = PedidoVenda.query \
        .filter(PedidoVenda.status.in_(
<<<<<<< HEAD
            ['recebido','produção','pronto','enviado']
        )).count()
=======
        ['recebido', 'produção', 'pronto', 'enviado']
    )).count()
>>>>>>> e304e52 (commit ajuste flask)

    vendas_mes = db.session.query(
        func.coalesce(func.sum(PedidoVenda.valor_pedido), 0)
    ).filter(
<<<<<<< HEAD
        func.extract('year', PedidoVenda.data_pedido)  == datetime.now().year,
=======
        func.extract('year', PedidoVenda.data_pedido) == datetime.now().year,
>>>>>>> e304e52 (commit ajuste flask)
        func.extract('month', PedidoVenda.data_pedido) == datetime.now().month
    ).scalar()

    return render_template('gestao.html',
<<<<<<< HEAD
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
        vendas_mes=vendas_mes
    )

# ── Formulários “+ Novo” ───────────────────────────────────────────
@views.route('/gestao/mp/novo', methods=['GET','POST'])
=======
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
                           vendas_mes=vendas_mes
                           )


# ── Formulários “+ Novo” ───────────────────────────────────────────
@views.route('/gestao/mp/novo', methods=['GET', 'POST'])
>>>>>>> e304e52 (commit ajuste flask)
@login_required
def nova_materia_prima():
    if request.method == 'POST':
        m = MateriaPrima(
<<<<<<< HEAD
            codigo_item         = request.form['codigo_item'],
            tipo_material       = request.form['tipo_material'],
            unidade             = request.form['unidade'],
            quantidade_estoque  = float(request.form['quantidade_estoque']),
            ponto_reposicao     = float(request.form['ponto_reposicao']),
            fornecedor          = request.form.get('fornecedor'),
            data_ultima_entrada = date.fromisoformat(request.form['data_ultima_entrada']),
            observacoes         = request.form.get('observacoes')
=======
            codigo_item=request.form['codigo_item'],
            tipo_material=request.form['tipo_material'],
            unidade=request.form['unidade'],
            quantidade_estoque=float(request.form['quantidade_estoque']),
            ponto_reposicao=float(request.form['ponto_reposicao']),
            fornecedor=request.form.get('fornecedor'),
            data_ultima_entrada=date.fromisoformat(request.form['data_ultima_entrada']),
            observacoes=request.form.get('observacoes')
>>>>>>> e304e52 (commit ajuste flask)
        )
        db.session.add(m)
        db.session.commit()
        flash('Matéria-prima cadastrada!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('nova_materia_prima.html', user=current_user)

<<<<<<< HEAD
@views.route('/gestao/pa/novo', methods=['GET','POST'])
=======

@views.route('/gestao/pa/novo', methods=['GET', 'POST'])
>>>>>>> e304e52 (commit ajuste flask)
@login_required
def novo_produto_acabado():
    if request.method == 'POST':
        p = ProdutoAcabado(
<<<<<<< HEAD
            codigo_faca            = request.form['codigo_faca'],
            tipo                   = request.form['tipo'],
            material_lamina        = request.form['material_lamina'],
            material_cabo          = request.form['material_cabo'],
            quantidade_disponivel  = int(request.form['quantidade_disponivel']),
            quantidade_reservada   = int(request.form['quantidade_reservada']),
            quantidade_vendida_mes = int(request.form['quantidade_vendida_mes']),
            observacoes            = request.form.get('observacoes')
=======
            codigo_faca=request.form['codigo_faca'],
            tipo=request.form['tipo'],
            material_lamina=request.form['material_lamina'],
            material_cabo=request.form['material_cabo'],
            quantidade_disponivel=int(request.form['quantidade_disponivel']),
            quantidade_reservada=int(request.form['quantidade_reservada']),
            quantidade_vendida_mes=int(request.form['quantidade_vendida_mes']),
            observacoes=request.form.get('observacoes')
>>>>>>> e304e52 (commit ajuste flask)
        )
        db.session.add(p)
        db.session.commit()
        flash('Produto acabado cadastrado!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('novo_produto_acabado.html', user=current_user)

<<<<<<< HEAD
@views.route('/gestao/pv/novo', methods=['GET','POST'])
@login_required
def novo_pedido_venda():
    if request.method == 'POST':
        ped = PedidoVenda(
            numero_pedido           = request.form['numero_pedido'],
            nome_cliente            = request.form['nome_cliente'],
            produtos_solicitados    = request.form['produtos_solicitados'],
            personalizacao          = bool(request.form.get('personalizacao')),
            detalhes_personalizacao = request.form.get('detalhes_personalizacao'),
            data_pedido             = date.fromisoformat(request.form['data_pedido']),
            status                  = request.form['status'],
            data_prevista_entrega   = date.fromisoformat(request.form['data_prevista_entrega']),
            valor_pedido            = float(request.form['valor_pedido']),
            observacoes             = request.form.get('observacoes')
=======

@views.route('/gestao/pv/novo', methods=['GET', 'POST'])
@login_required
def novo_pedido_venda():
    # sempre carregue a lista de produtos acabados (oferecidos)
    produtos = ProdutoAcabado.query.all()

    if request.method == 'POST':
        # pega o produto selecionado e a quantidade via form
        produto_id = int(request.form['produto_id'])
        produto = ProdutoAcabado.query.get_or_404(produto_id)
        quantidade = int(request.form['quantidade'])

        # monta a string produtos_solicitados com código x qtde
        solicitacao = f"{produto.codigo_faca} × {quantidade}"

        ped = PedidoVenda(
            numero_pedido=request.form['numero_pedido'],
            nome_cliente=request.form['nome_cliente'],
            produtos_solicitados=solicitacao,
            personalizacao=bool(request.form.get('personalizacao')),
            detalhes_personalizacao=request.form.get('detalhes_personalizacao'),
            data_pedido=date.fromisoformat(request.form['data_pedido']),
            status=request.form['status'],
            data_prevista_entrega=date.fromisoformat(request.form['data_prevista_entrega']),
            valor_pedido=float(request.form['valor_pedido']),
            observacoes=request.form.get('observacoes')
>>>>>>> e304e52 (commit ajuste flask)
        )
        db.session.add(ped)
        db.session.commit()
        flash('Pedido/venda cadastrado!', 'success')
        return redirect(url_for('views.gestao'))
<<<<<<< HEAD
    return render_template('novo_pedido_venda.html', user=current_user)

@views.route('/gestao/os/novo', methods=['GET','POST'])
=======

    # GET: renderiza o form, passando lista de produtos
    return render_template('novo_pedido_venda.html', user=current_user, produtos=produtos, date=date)


@views.route('/gestao/os/novo', methods=['GET', 'POST'])
>>>>>>> e304e52 (commit ajuste flask)
@login_required
def nova_ordem_servico():
    if request.method == 'POST':
        os_ = OrdemServico(
<<<<<<< HEAD
            numero_os               = request.form['numero_os'],
            produto_id              = int(request.form['produto_id']),
            quantidade              = int(request.form['quantidade']),
            materias_necessarios   = request.form['materiais_necessarios'],
            data_inicio_producao    = date.fromisoformat(request.form['data_inicio_producao']),
            data_prevista_conclusao = date.fromisoformat(request.form['data_prevista_conclusao']),
            responsavel             = request.form['responsavel'],
            status                  = request.form['status']
=======
            numero_os=request.form['numero_os'],
            produto_id=int(request.form['produto_id']),
            quantidade=int(request.form['quantidade']),
            materiais_necessarios=request.form['materiais_necessarios'],
            data_inicio_producao=date.fromisoformat(request.form['data_inicio_producao']),
            data_prevista_conclusao=date.fromisoformat(request.form['data_prevista_conclusao']),
            responsavel=request.form['responsavel'],
            status=request.form['status']
>>>>>>> e304e52 (commit ajuste flask)
        )
        db.session.add(os_)
        raw = request.form['materiais_necessarios']
        pairs = re.findall(r'(\w+)\s*[x×]\s*([\d\.]+)', raw)
        if not pairs:
            flash("Formato inválido em Materiais necessários.", 'error')
            db.session.rollback()
            return redirect(url_for('views.nova_ordem_servico'))
        for code, qty_text in pairs:
            consumed = float(qty_text)
            mat = MateriaPrima.query.filter_by(codigo_item=code).first()
            if not mat:
                flash(f"Matéria-prima \u201C{code}\u201D não encontrada.", 'error')
                db.session.rollback()
                return redirect(url_for('views.nova_ordem_servico'))
            mat.quantidade_estoque = max(mat.quantidade_estoque - consumed, 0.0)
            db.session.add(mat)
        db.session.commit()
        flash('Ordem de serviço cadastrada e estoque atualizado!', 'success')
        return redirect(url_for('views.gestao'))
    produtos = ProdutoAcabado.query.all()
    return render_template('nova_ordem_servico.html', user=current_user, produtos=produtos)

<<<<<<< HEAD
@views.route('/gestao/reposicao/novo', methods=['GET','POST'])
=======

@views.route('/gestao/reposicao/novo', methods=['GET', 'POST'])
>>>>>>> e304e52 (commit ajuste flask)
@login_required
def nova_reposicao_materia_prima():
    if request.method == 'POST':
        rp = ReposicaoMateriaPrima(
<<<<<<< HEAD
            materia_id              = int(request.form['materia_id']),
            quantidade_reposicao    = float(request.form['quantidade_reposicao']),
            data_solicitacao        = date.fromisoformat(request.form['data_solicitacao']),
            data_previsao_reposicao = date.fromisoformat(request.form['data_previsao_reposicao']),
            fornecedor              = request.form.get('fornecedor'),
            status                  = request.form['status'],
            observacoes             = request.form.get('observacoes')
=======
            materia_id=int(request.form['materia_id']),
            quantidade_reposicao=float(request.form['quantidade_reposicao']),
            data_solicitacao=date.fromisoformat(request.form['data_solicitacao']),
            data_previsao_reposicao=date.fromisoformat(request.form['data_previsao_reposicao']),
            fornecedor=request.form.get('fornecedor'),
            status=request.form['status'],
            observacoes=request.form.get('observacoes')
>>>>>>> e304e52 (commit ajuste flask)
        )
        db.session.add(rp)
        mat = MateriaPrima.query.get(rp.materia_id)
        if mat:
            mat.quantidade_estoque += rp.quantidade_reposicao
            db.session.add(mat)
        db.session.commit()
        flash('Requisição de reposição cadastrada e estoque atualizado!', 'success')
        return redirect(url_for('views.gestao'))
    materias = MateriaPrima.query.all()
<<<<<<< HEAD
    return render_template(
        'nova_reposicao.html',
        user=current_user,
        materias=materias,
        date=date
    )

@views.route('/gestao/reposicao/edit/<int:rp_id>', methods=['GET','POST'])
=======
    return render_template('nova_reposicao.html',user=current_user,materias=materias,date=date)


@views.route('/gestao/reposicao/edit/<int:rp_id>', methods=['GET', 'POST'])
>>>>>>> e304e52 (commit ajuste flask)
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
<<<<<<< HEAD
                mat.quantidade_estoque = max( mat.quantidade_estoque - rp.quantidade_reposicao, 0.0 )
=======
                mat.quantidade_estoque = max(mat.quantidade_estoque - rp.quantidade_reposicao, 0.0)
>>>>>>> e304e52 (commit ajuste flask)
            db.session.add(mat)

        db.session.commit()
        flash(f'Status da reposição #{rp.id} atualizado para "{rp.status}" e estoque ajustado.', 'success')
        return redirect(url_for('views.gestao'))

    return render_template('edit_reposicao.html', user=current_user, reposicao=rp)
<<<<<<< HEAD
=======

@views.route('/gestao/pv/edit/<int:ped_id>', methods=['GET','POST'])
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
>>>>>>> e304e52 (commit ajuste flask)
