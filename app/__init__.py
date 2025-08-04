from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///default.db')

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from .auth.models import get_user_by_id
        return get_user_by_id(user_id)

    with app.app_context():
        from .models import ExampleGlobalModel
        from .auth.models import User

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth.auth_bp import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    return app
