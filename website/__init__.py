# website/__init__.py

import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth

# — filenames (without paths) —
DB_NOTES      = "database.db"
DB_MANAGEMENT = "management"

# — custom SQLAlchemy that remaps the “management” bind per-user —
class TenantSQLAlchemy(SQLAlchemy):
    def get_engine(self, app=None, bind=None):
        app = app or self.get_app()

        # whenever a model uses __bind_key__ = 'management'
        # and a user is logged in, override that bind to per-user file
        if bind == DB_MANAGEMENT and current_user.is_authenticated:
            db_path = os.path.join(app.instance_path,
                                   f"{DB_MANAGEMENT}_{current_user.id}.db")
            uri     = f"sqlite:///{db_path}"
            # ensure the binds dict exists and update the "management" entry
            binds = app.config.setdefault('SQLALCHEMY_BINDS', {})
            binds[DB_MANAGEMENT] = uri
        return super().get_engine(app, bind)

# — initialize extensions —
db            = TenantSQLAlchemy()
login_manager = LoginManager()
oauth         = OAuth()

# — allowed image extensions helper —
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def create_app():
    # enable instance folder config
    app = Flask(__name__, instance_relative_config=True)

    # ensure instance folder exists (where we'll store the DBs)
    os.makedirs(app.instance_path, exist_ok=True)

    # ── General config ──────────────────────────────────────────────
    app.config['SECRET_KEY']                = os.environ.get('SECRET_KEY', '#maiorcampeaodobrasil')
    # default (notes) DB in instance folder
    app.config['SQLALCHEMY_DATABASE_URI']   = f"sqlite:///{os.path.join(app.instance_path, DB_NOTES)}"
    # initial management bind placeholder (overwritten per request)
    app.config['SQLALCHEMY_BINDS'] = {
        DB_MANAGEMENT: f"sqlite:///{os.path.join(app.instance_path, DB_MANAGEMENT)}.db"
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Google OAuth2 config ────────────────────────────────────────
    app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

    # ── Initialize extensions ────────────────────────────────────────
    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope':'openid email profile'}
    )

    # ── User loader ──────────────────────────────────────────────────
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register blueprints ──────────────────────────────────────────
    from .views import views
    from .auth  import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)

    # ── Create only the default (notes) tables at startup ─────────────
    with app.app_context():
        # this uses the default engine (database.db) only
        db.Model.metadata.create_all(bind=db.engine)

    return app
