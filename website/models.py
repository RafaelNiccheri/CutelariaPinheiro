# website/models.py

from datetime import date
from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

# ── Gestão Models (bind='management') ────────────────────────────

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

    id                     = db.Column(db.Integer, primary_key=True)
    codigo_faca            = db.Column(db.String(50), unique=True, nullable=False)
    tipo                   = db.Column(db.String(50), nullable=False)
    material_lamina        = db.Column(db.String(50), nullable=False)
    material_cabo          = db.Column(db.String(50), nullable=False)
    quantidade_disponivel  = db.Column(db.Integer, nullable=False)
    quantidade_reservada   = db.Column(db.Integer, nullable=False)
    quantidade_vendida_mes = db.Column(db.Integer, nullable=False)
    observacoes            = db.Column(db.Text, nullable=True)

    # Relação com OrdemServico (produções em andamento)
    ordens = db.relationship(
        'OrdemServico',
        back_populates='produto',
        cascade='all, delete-orphan',
        lazy=True
    )

    # Relação com imagens de produto
    images = db.relationship(
        'ProductImage',
        back_populates='produto',
        cascade='all, delete-orphan',
        lazy=True
    )

    vendas_normais = db.relationship(
        'VendaNormal',
        back_populates = 'produto',
        cascade = 'all, delete-orphan',
        lazy = True
                    )

    # Relação com Inventario (itens concluídos)
    inventario = db.relationship(
        'Inventario',
        back_populates='produto',
        cascade='all, delete-orphan',
        lazy=True
    )

class VendaNormal(db.Model):
    __bind_key__  = 'management'
    __tablename__ = 'venda_normal'

    id          = db.Column(db.Integer, primary_key=True)
    produto_id  = db.Column(
        db.Integer,
        db.ForeignKey('produto_acabado.id'),
        nullable=False
    )
    cliente     = db.Column(db.String(100), nullable=False)
    quantidade  = db.Column(db.Integer, nullable=False)
    valor_venda = db.Column(db.Float, nullable=False)
    data_venda  = db.Column(db.Date, default=date.today, nullable=False)

    produto = db.relationship(
        'ProdutoAcabado',
        back_populates='vendas_normais'
    )

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
    produto                  = db.relationship('ProdutoAcabado', back_populates='ordens')
    quantidade               = db.Column(db.Integer, nullable=False)
    materiais_necessarios    = db.Column(db.Text, nullable=False)
    data_inicio_producao     = db.Column(db.Date, default=date.today)
    data_prevista_conclusao  = db.Column(db.Date, nullable=True)
    responsavel              = db.Column(db.String(100), nullable=False)

    # só o status de produção, sem campos de venda aqui
    status                   = db.Column(db.String(50), nullable=False, default='produção')

class ReposicaoMateriaPrima(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'reposicao_materia_prima'
    id                       = db.Column(db.Integer, primary_key=True)
    materia_id               = db.Column(db.Integer, db.ForeignKey('materia_prima.id'), nullable=False)
    quantidade_reposicao     = db.Column(db.Float, nullable=False)
    data_solicitacao         = db.Column(db.Date, nullable=False)
    data_previsao_reposicao  = db.Column(db.Date, nullable=True)
    fornecedor               = db.Column(db.String(100), nullable=True)
    status                   = db.Column(db.String(50), nullable=False)
    observacoes              = db.Column(db.Text, nullable=True)

    materia = db.relationship('MateriaPrima', backref=db.backref('reposicoes', lazy=True))

class ProductImage(db.Model):
    __bind_key__ = 'management'
    __tablename__ = 'product_image'
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('produto_acabado.id'), nullable=False)
    filename   = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)

    produto    = db.relationship('ProdutoAcabado', back_populates='images')

ProdutoAcabado.images = db.relationship(
    'ProductImage',
    order_by=ProductImage.id,
    back_populates='produto',
    cascade='all, delete-orphan',
    lazy=True
)

class Inventario(db.Model):
    __bind_key__  = 'management'
    __tablename__ = 'inventario'

    id            = db.Column(db.Integer, primary_key=True)
    produto_id    = db.Column(db.Integer,
                              db.ForeignKey('produto_acabado.id'),
                              nullable=False)
    quantidade    = db.Column(db.Integer, nullable=False)
    data_entrada  = db.Column(db.Date, default=date.today, nullable=False)

    produto       = db.relationship('ProdutoAcabado',
                                    back_populates='inventario')
