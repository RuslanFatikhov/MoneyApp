#!/usr/bin/env python3
"""
Простой тест системы аутентификации
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.models import create_user, verify_user
from app.auth.validators import is_valid_email, is_valid_password

def test_validators():
    print("🧪 Тестируем валидаторы...")
    
    # Тест email
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("invalid-email") == False
    assert is_valid_email("@example.com") == False
    print("✅ Email валидация работает")
    
    # Тест пароля
    valid, msg = is_valid_password("password123")
    assert valid == True
    
    valid, msg = is_valid_password("123")
    assert valid == False
    assert "8 символов" in msg
    
    valid, msg = is_valid_password("password")
    assert valid == False
    assert "цифры" in msg
    
    valid, msg = is_valid_password("12345678")
    assert valid == False
    assert "буквы" in msg
    
    print("✅ Пароль валидация работает")

def test_auth_flow():
    print("🧪 Тестируем процесс аутентификации...")
    
    # Инициализируем БД если нужно
    if not os.path.exists('database/finance.db'):
        from init_db import init_database
        init_database()
    
    test_email = "test@example.com"
    test_password = "testpass123"
    
    # Регистрация
    success, result = create_user(test_email, test_password)
    if success:
        print("✅ Пользователь создан успешно")
        user_id = result
    else:
        if "уже зарегистрирован" in result:
            print("ℹ️ Пользователь уже существует")
        else:
            print(f"❌ Ошибка создания: {result}")
            return
    
    # Проверка входа
    success, result = verify_user(test_email, test_password)
    if success:
        print("✅ Вход выполнен успешно")
    else:
        print(f"❌ Ошибка входа: {result}")
        return
    
    # Проверка неверного пароля
    success, result = verify_user(test_email, "wrongpass")
    if not success:
        print("✅ Неверный пароль отклонен")
    else:
        print("❌ Неверный пароль принят!")
        return

def main():
    print("🚀 Запуск тестов аутентификации")
    print("=" * 40)
    
    try:
        test_validators()
        test_auth_flow()
        print("=" * 40)
        print("🎉 Все тесты прошли успешно!")
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()