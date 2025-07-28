from app import create_app
import os
import json

# Создание необходимых директорий
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('app/templates', exist_ok=True)
os.makedirs('app/static/js', exist_ok=True)
os.makedirs('static/data', exist_ok=True)
os.makedirs('app/accounts', exist_ok=True)

# Создание JSON файлов если их нет
def create_json_files():
    # banks.json
    banks_file = 'static/data/banks.json'
    if not os.path.exists(banks_file):
        banks_data = {
            "banks": [
                {"id": "kaspi", "name": "Kaspi Bank", "country": "KZ", "color": "#F44336"},
                {"id": "halyk", "name": "Народный Банк", "country": "KZ", "color": "#4CAF50"},
                {"id": "kazkommertsbank", "name": "Казкоммерцбанк", "country": "KZ", "color": "#1E88E5"},
                {"id": "other", "name": "Другой банк", "country": "", "color": "#9E9E9E"}
            ]
        }
        with open(banks_file, 'w', encoding='utf-8') as f:
            json.dump(banks_data, f, ensure_ascii=False, indent=2)
    
    # currencies.json
    currencies_file = 'static/data/currencies.json'
    if not os.path.exists(currencies_file):
        currencies_data = {
            "currencies": [
                {"code": "KZT", "name": "Казахстанский тенге", "symbol": "₸", "default": True},
                {"code": "USD", "name": "Доллар США", "symbol": "$"},
                {"code": "EUR", "name": "Евро", "symbol": "€"},
                {"code": "RUB", "name": "Российский рубль", "symbol": "₽"}
            ]
        }
        with open(currencies_file, 'w', encoding='utf-8') as f:
            json.dump(currencies_data, f, ensure_ascii=False, indent=2)

create_json_files()

app = create_app()

if __name__ == '__main__':
    print("🚀 Запуск FinanceTracker PWA...")
    print("📱 Сервис будет доступен по адресу: http://localhost:5002")
    print("🔥 Режим разработки: включен")
    print("💳 Модуль счетов: подключен")
    print("=" * 50)
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002,
        threaded=True
    )