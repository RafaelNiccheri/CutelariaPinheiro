# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

DB_NOTES = "database.db"
DB_MANAGEMENT = "management.db"

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ─── Configurações gerais ───────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '#maiorcampeaodobrasil')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NOTES}"
    app.config['SQLALCHEMY_BINDS'] = {
        'management': f"sqlite:///{DB_MANAGEMENT}"
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ─── Credenciais OAuth (Google) ─────────────────────────────────
    app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

    # ─── Inicializa extensões ────────────────────────────────────────
    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # ─── User Loader ─────────────────────────────────────────────────
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ─── Registra Blueprints ─────────────────────────────────────────
    from .views import views
    from .auth  import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)

    # ─── Cria todas as tabelas (default + binds) ─────────────────────
    with app.app_context():
        db.create_all()
        print("🏗️  Todas as tabelas foram criadas (default + management)!")

    return app
