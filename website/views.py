# website/views.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from datetime import date, datetime
from sqlalchemy import func
from .models import (
    Note,
    User,
    MateriaPrima,
    ProdutoAcabado,
    PedidoVenda,
    OrdemServico
)

views = Blueprint('views', __name__)

# ── Notes Home & Create ────────────────────────────────────────────────
@views.route('/', methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        note_text = request.form.get('note')
        if not note_text or len(note_text) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note_text, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, notes=notes)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    note = Note.query.get(data.get('noteId'))
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({})

# ── Gestão Dashboard ───────────────────────────────────────────────────
@views.route('/gestao')
@login_required
def gestao():
    # Core lists
    materias   = MateriaPrima.query.all()
    produtos   = ProdutoAcabado.query.all()
    pedidos    = PedidoVenda.query.all()
    ordens     = OrdemServico.query.all()

    # Alertas / indicadores
    itens_baixo_estoque = MateriaPrima.query\
        .filter(MateriaPrima.quantidade_estoque < MateriaPrima.ponto_reposicao)\
        .all()

    pedidos_vencidos = PedidoVenda.query\
        .filter(
            PedidoVenda.data_prevista_entrega < date.today(),
            PedidoVenda.status != 'entregue'
        ).all()

    producoes_atrasadas = OrdemServico.query\
        .filter(
            OrdemServico.data_prevista_conclusao < date.today(),
            OrdemServico.status != 'concluida'
        ).all()

    total_pedidos_andamento = PedidoVenda.query\
        .filter(PedidoVenda.status.in_(
            ['recebido','produção','pronto','enviado']
        )).count()

    vendas_mes = db.session.query(
        func.coalesce(func.sum(PedidoVenda.valor_pedido), 0)
    ).filter(
        func.extract('year', PedidoVenda.data_pedido)  == datetime.now().year,
        func.extract('month', PedidoVenda.data_pedido) == datetime.now().month
    ).scalar()

    return render_template('gestao.html',
        user=current_user,
        materias=materias,
        produtos=produtos,
        pedidos=pedidos,
        ordens=ordens,
        itens_baixo_estoque=itens_baixo_estoque,
        pedidos_vencidos=pedidos_vencidos,
        producoes_atrasadas=producoes_atrasadas,
        total_pedidos_andamento=total_pedidos_andamento,
        vendas_mes=vendas_mes
    )

# ── “+ Novo” Routes for Gestão ─────────────────────────────────────────
@views.route('/gestao/mp/novo', methods=['GET','POST'])
@login_required
def nova_materia_prima():
    if request.method == 'POST':
        m = MateriaPrima(
            codigo_item         = request.form['codigo_item'],
            tipo_material       = request.form['tipo_material'],
            unidade             = request.form['unidade'],
            quantidade_estoque  = float(request.form['quantidade_estoque']),
            ponto_reposicao     = float(request.form['ponto_reposicao']),
            fornecedor          = request.form.get('fornecedor'),
            data_ultima_entrada = date.fromisoformat(request.form['data_ultima_entrada']),
            observacoes         = request.form.get('observacoes')
        )
        db.session.add(m)
        db.session.commit()
        flash('Matéria-prima cadastrada com sucesso!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('nova_materia_prima.html', user=current_user)

@views.route('/gestao/pa/novo', methods=['GET','POST'])
@login_required
def novo_produto_acabado():
    if request.method == 'POST':
        p = ProdutoAcabado(
            codigo_faca            = request.form['codigo_faca'],
            tipo                   = request.form['tipo'],
            material_lamina        = request.form['material_lamina'],
            material_cabo          = request.form['material_cabo'],
            quantidade_disponivel  = int(request.form['quantidade_disponivel']),
            quantidade_reservada   = int(request.form['quantidade_reservada']),
            quantidade_vendida_mes = int(request.form['quantidade_vendida_mes']),
            observacoes            = request.form.get('observacoes')
        )
        db.session.add(p)
        db.session.commit()
        flash('Produto acabado cadastrado com sucesso!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('novo_produto_acabado.html', user=current_user)

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
        )
        db.session.add(ped)
        db.session.commit()
        flash('Pedido/venda cadastrado com sucesso!', 'success')
        return redirect(url_for('views.gestao'))
    return render_template('novo_pedido_venda.html', user=current_user)

@views.route('/gestao/os/novo', methods=['GET','POST'])
@login_required
def nova_ordem_servico():
    if request.method == 'POST':
        os_ = OrdemServico(
            numero_os                = request.form['numero_os'],
            produto_id               = int(request.form['produto_id']),
            quantidade               = int(request.form['quantidade']),
            materiais_necessarios    = request.form['materiais_necessarios'],
            data_inicio_producao     = date.fromisoformat(request.form['data_inicio_producao']),
            data_prevista_conclusao  = date.fromisoformat(request.form['data_prevista_conclusao']),
            responsavel              = request.form['responsavel'],
            status                   = request.form['status']
        )
        db.session.add(os_)
        db.session.commit()
        flash('Ordem de serviço cadastrada com sucesso!', 'success')
        return redirect(url_for('views.gestao'))

    produtos = ProdutoAcabado.query.all()
    return render_template('nova_ordem_servico.html', user=current_user, produtos=produtos)
