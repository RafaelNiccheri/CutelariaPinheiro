# website/models.py

from datetime import date
from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

class Note(db.Model):
    __tablename__ = 'note'
    id      = db.Column(db.Integer, primary_key=True)
    data    = db.Column(db.String(10000))
    date    = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    notes      = db.relationship('Note', backref='user', lazy=True)

# ── Modelos do Sistema de Gestão (bind 'management') ──────────────────────

class MateriaPrima(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'materia_prima'
    id                  = db.Column(db.Integer, primary_key=True)
    codigo_item         = db.Column(db.String(50), unique=True, nullable=False)
    tipo_material       = db.Column(db.String(50), nullable=False)
    unidade             = db.Column(db.String(10), nullable=False)
    quantidade_estoque  = db.Column(db.Float, nullable=False)
    ponto_reposicao     = db.Column(db.Float, nullable=False)
    fornecedor          = db.Column(db.String(100), nullable=True)
    data_ultima_entrada = db.Column(db.Date, default=date.today)
    observacoes         = db.Column(db.Text, nullable=True)

class ProdutoAcabado(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'produto_acabado'
    id                      = db.Column(db.Integer, primary_key=True)
    codigo_faca             = db.Column(db.String(50), unique=True, nullable=False)
    tipo                    = db.Column(db.String(50), nullable=False)
    material_lamina         = db.Column(db.String(50), nullable=False)
    material_cabo           = db.Column(db.String(50), nullable=False)
    quantidade_disponivel   = db.Column(db.Integer, nullable=False)
    quantidade_reservada    = db.Column(db.Integer, nullable=False)
    quantidade_vendida_mes  = db.Column(db.Integer, nullable=False)
    observacoes             = db.Column(db.Text, nullable=True)

class PedidoVenda(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'pedido_venda'
    id                       = db.Column(db.Integer, primary_key=True)
    numero_pedido            = db.Column(db.String(50), unique=True, nullable=False)
    nome_cliente             = db.Column(db.String(100), nullable=False)
    produtos_solicitados     = db.Column(db.Text, nullable=False)
    personalizacao           = db.Column(db.Boolean, default=False)
    detalhes_personalizacao  = db.Column(db.Text, nullable=True)
    data_pedido              = db.Column(db.Date, default=date.today)
    status                   = db.Column(db.String(50), nullable=False)
    data_prevista_entrega    = db.Column(db.Date, nullable=True)
    valor_pedido             = db.Column(db.Float, nullable=False)
    observacoes              = db.Column(db.Text, nullable=True)

class OrdemServico(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'ordem_servico'
    id                       = db.Column(db.Integer, primary_key=True)
    numero_os                = db.Column(db.String(50), unique=True, nullable=False)
    produto_id               = db.Column(db.Integer, db.ForeignKey('produto_acabado.id'), nullable=False)
    produto                  = db.relationship('ProdutoAcabado', backref=db.backref('ordens', lazy=True))
    quantidade               = db.Column(db.Integer, nullable=False)
    materiais_necessarios    = db.Column(db.Text, nullable=False)
    data_inicio_producao     = db.Column(db.Date, default=date.today)
    data_prevista_conclusao  = db.Column(db.Date, nullable=True)
    responsavel              = db.Column(db.String(100), nullable=False)
    status                   = db.Column(db.String(50), nullable=False)
