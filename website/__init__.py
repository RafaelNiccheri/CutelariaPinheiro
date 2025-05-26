# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # ── Configure upload path to website/static/uploads ─────────
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # ── General config ────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude_esta_chave')

    # Default (and only) DB
    db_path = os.path.join(app.instance_path, 'management.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ALSO declare a bind so that __bind_key__ = 'management' works
    app.config['SQLALCHEMY_BINDS'] = {
        'management': app.config['SQLALCHEMY_DATABASE_URI']
    }

    # ── Initialize extensions ─────────────────────────────────────────
    db.init_app(app)

    # ── Register your blueprints ──────────────────────────────────────
    from .views import views
    app.register_blueprint(views)

    # ── Create all tables (default + binds) if they don't exist ──────
    with app.app_context():
        db.create_all()

    return app
