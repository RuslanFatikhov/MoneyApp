from flask import Flask
import secrets
import os

def create_app():
    # Указываем правильные пути для шаблонов И статических файлов
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Конфигурация
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    
    # Создание необходимых директорий
    os.makedirs('uploads/temp', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    os.makedirs('static/data', exist_ok=True)
    
    # Регистрация blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    from app.accounts.routes import accounts_bp
    app.register_blueprint(accounts_bp)
    
    return app