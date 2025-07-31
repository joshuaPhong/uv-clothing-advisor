# app/__init__.py

import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
	app = Flask(__name__)
	app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

	from .routes import main_bp
	app.register_blueprint(main_bp)
	from app.auth.auth_routes import auth_bp
	app.register_blueprint(auth_bp, url_prefix='/auth')

	return app


