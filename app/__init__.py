from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config.from_object(Config)
    
    # Простой маршрут для тестирования
    @app.route('/')
    def index():
        return '''
        <h1>🏦 FinanceTracker PWA</h1>
        <p>Сервис успешно запущен!</p>
        <p>Версия: 1.0.0</p>
        <hr>
        <h3>Следующие шаги:</h3>
        <ul>
            <li>✅ Базовая структура создана</li>
            <li>✅ Flask сервер запущен</li>
            <li>⏳ Настройка базы данных</li>
            <li>⏳ Создание моделей</li>
            <li>⏳ Авторизация</li>
            <li>⏳ OCR интеграция</li>
            <li>⏳ PWA функциональность</li>
        </ul>
        '''
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Finance Tracker is running'}
    
    return app