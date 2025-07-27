import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-finance-tracker-2024'
    
    # Базовые настройки
    DEBUG = True
    TESTING = False
    
    # Настройки файлов
    UPLOAD_FOLDER = 'uploads/temp'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Настройки приложения
    APP_NAME = 'FinanceTracker'
    APP_VERSION = '1.0.0'