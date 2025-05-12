# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db    = SQLAlchemy()
oauth = OAuth()

DB_NOTES      = "database.db"
DB_MANAGEMENT = "management.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '#maiorcampeaodobrasil'

    # Banco de notas (default)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NOTES}"
    # Banco de gestão (bind 'management')
    app.config['SQLALCHEMY_BINDS'] = {
        'management': f"sqlite:///{DB_MANAGEMENT}"
    }

    # Credenciais Google OAuth
    app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

    # Inicializa extensões
    db.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Carregador de usuário
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registro de blueprints
    from .views import views
    from .auth  import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)

    # Cria os bancos se ainda não existirem
    create_notes_database(app)
    create_management_database(app)

    return app

def create_notes_database(app):
    """Cria apenas o banco de notas (database.db) se não existir."""
    if not path.exists('website/' + DB_NOTES):
        with app.app_context():
            engine = db.engine  # engine padrão
            from .models import Note, User
            Note.__table__.create(bind=engine, checkfirst=True)
            User.__table__.create(bind=engine, checkfirst=True)
        print(f'Created {DB_NOTES}!')

def create_management_database(app):
    """Cria apenas o banco de gestão (management.db) se não existir."""
    if not path.exists('website/' + DB_MANAGEMENT):
        with app.app_context():
            engine = db.get_engine(bind='management')
            from .models import MateriaPrima, ProdutoAcabado, PedidoVenda, OrdemServico
            for model in (MateriaPrima, ProdutoAcabado, PedidoVenda, OrdemServico):
                model.__table__.create(bind=engine, checkfirst=True)
        print(f'Created {DB_MANAGEMENT}!')
