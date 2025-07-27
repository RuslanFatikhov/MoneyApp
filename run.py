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

# Создание необходимых директорий
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('app/templates', exist_ok=True)
os.makedirs('app/static/js', exist_ok=True)

app = create_app()

if __name__ == '__main__':
    print("🚀 Запуск FinanceTracker PWA...")
    print("📱 Сервис будет доступен по адресу: http://localhost:5002")
    print("🔥 Режим разработки: включен")
    print("=" * 50)
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002,
        threaded=True
    )