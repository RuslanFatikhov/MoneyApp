from flask import Flask
import secrets
import os

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    
    # Регистрация blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app