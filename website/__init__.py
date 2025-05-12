# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
oauth = OAuth()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '#maiorcampeaodobrasil'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # ── Google OAuth2 settings ───────────────────────────────────────────────
    app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

    db.init_app(app)

    # Initialize and register our OAuth client
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={ 'scope': 'openid email profile' }
    )

    # ── Flask-Login setup ────────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register blueprints ───────────────────────────────────────────────────
    from .views import views
    from .auth  import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
