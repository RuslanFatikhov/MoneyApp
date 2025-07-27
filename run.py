from app import create_app
import os

# Создание необходимых директорий
os.makedirs('uploads/temp', exist_ok=True)
os.makedirs('database', exist_ok=True)

app = create_app()

if __name__ == '__main__':
    print("🚀 Запуск FinanceTracker PWA...")
    print("📱 Сервис будет доступен по адресу: http://localhost:5000")
    print("🔥 Режим разработки: включен")
    print("=" * 50)
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5002,
        threaded=True
    )