#!/usr/bin/env python3
"""
Тест функционала управления счетами
"""

import sys
import os
import json

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_json_files():
    print("🧪 Тестируем JSON справочники...")
    
    # Проверяем banks.json
    banks_file = 'static/data/banks.json'
    if os.path.exists(banks_file):
        with open(banks_file, 'r', encoding='utf-8') as f:
            banks_data = json.load(f)
            assert 'banks' in banks_data
            assert len(banks_data['banks']) > 0
            print("✅ banks.json корректен")
    else:
        print("❌ banks.json не найден")
    
    # Проверяем currencies.json
    currencies_file = 'static/data/currencies.json'
    if os.path.exists(currencies_file):
        with open(currencies_file, 'r', encoding='utf-8') as f:
            currencies_data = json.load(f)
            assert 'currencies' in currencies_data
            assert len(currencies_data['currencies']) > 0
            print("✅ currencies.json корректен")
    else:
        print("❌ currencies.json не найден")

def test_accounts_models():
    print("🧪 Тестируем модели счетов...")
    
    # Инициализируем БД если нужно
    if not os.path.exists('database/finance.db'):
        from init_db import init_database
        init_database()
    
    try:
        from app.accounts.models import (
            create_account, get_user_accounts, get_account_by_id,
            update_account, archive_account, restore_account
        )
        
        # Создаем тестового пользователя если нужно
        from app.auth.models import create_user
        
        test_email = "test_accounts@example.com"
        test_password = "testpass123"
        
        success, user_result = create_user(test_email, test_password)
        if success:
            user_id = user_result
            print(f"✅ Тестовый пользователь создан: ID {user_id}")
        else:
            if "уже зарегистрирован" in user_result:
                # Получаем ID существующего пользователя
                from app.auth.models import verify_user
                success, user_id = verify_user(test_email, test_password)
                if success:
                    print(f"ℹ️ Используем существующего пользователя: ID {user_id}")
                else:
                    print(f"❌ Ошибка получения пользователя: {user_result}")
                    return
            else:
                print(f"❌ Ошибка создания пользователя: {user_result}")
                return
        
        # Создаем тестовый счет
        success, account_result = create_account(
            user_id=user_id,
            name="Тестовый счет Kaspi",
            account_type="checking",
            currency="KZT",
            bank_id="kaspi",
            initial_balance=100000.0
        )
        
        if success:
            account_id = int(account_result)
            print(f"✅ Счет создан: ID {account_id}")
            
            # Получаем список счетов
            accounts = get_user_accounts(user_id)
            if accounts:
                print(f"✅ Получено счетов: {len(accounts)}")
                
                # Получаем конкретный счет
                account = get_account_by_id(account_id, user_id)
                if account:
                    print(f"✅ Счет найден: {account['name']}")
                    print(f"   Баланс: {account['current_balance']} {account['currency']}")
                    
                    # Обновляем счет
                    success, update_result = update_account(
                        account_id, user_id, name="Обновленный счет Kaspi"
                    )
                    if success:
                        print("✅ Счет обновлен")
                        
                        # Архивируем счет
                        success, archive_result = archive_account(account_id, user_id)
                        if success:
                            print("✅ Счет архивирован")
                            
                            # Восстанавливаем счет
                            success, restore_result = restore_account(account_id, user_id)
                            if success:
                                print("✅ Счет восстановлен")
                            else:
                                print(f"❌ Ошибка восстановления: {restore_result}")
                        else:
                            print(f"❌ Ошибка архивирования: {archive_result}")
                    else:
                        print(f"❌ Ошибка обновления: {update_result}")
                else:
                    print("❌ Счет не найден")
            else:
                print("❌ Счета не получены")
        else:
            print(f"❌ Ошибка создания счета: {account_result}")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

def test_file_structure():
    print("🧪 Проверяем структуру файлов...")
    
    required_files = [
        'app/accounts/__init__.py',
        'app/accounts/models.py',
        'app/accounts/routes.py',
        'templates/create_account.html',
        'templates/accounts.html',
        'static/js/create_account.js',
        'static/js/accounts.js'
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
            all_good = False
    
    return all_good

def main():
    print("🚀 Запуск тестов модуля счетов")
    print("=" * 50)
    
    try:
        # Создаем необходимые директории
        os.makedirs('static/data', exist_ok=True)
        os.makedirs('app/accounts', exist_ok=True)
        
        test_json_files()
        print()
        
        if test_file_structure():
            print()
            test_accounts_models()
        
        print("=" * 50)
        print("🎉 Тесты модуля счетов завершены!")
        print("💡 Теперь можно запустить: python run.py")
        print("🌐 И перейти на: http://localhost:5002")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()