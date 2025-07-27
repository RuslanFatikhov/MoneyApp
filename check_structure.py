#!/usr/bin/env python3
"""
Проверка структуры проекта
"""

import os

def check_file_exists(path, description):
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} - НЕ НАЙДЕН")
        return False

def check_project_structure():
    print("🔍 Проверка структуры проекта...")
    print("=" * 50)
    
    all_good = True
    
    # Основные файлы
    files_to_check = [
        ("run.py", "Точка входа"),
        ("init_db.py", "Инициализация БД"),
        ("requirements.txt", "Зависимости"),
        ("database/schema.sql", "Схема БД"),
        ("app/__init__.py", "Application Factory"),
        ("app/auth/__init__.py", "Пакет auth"),
        ("app/auth/models.py", "Модели аутентификации"),
        ("app/auth/validators.py", "Валидаторы"),
        ("app/auth/routes.py", "Маршруты аутентификации"),
        ("app/main/__init__.py", "Пакет main"),
        ("app/main/routes.py", "Основные маршруты")
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("=" * 50)
    
    # Проверка директорий
    dirs_to_check = [
        "app",
        "app/auth", 
        "app/main",
        "database"
    ]
    
    print("📁 Проверка директорий...")
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✅ Директория: {dir_path}")
        else:
            print(f"❌ Директория: {dir_path} - НЕ НАЙДЕНА")
            all_good = False
    
    print("=" * 50)
    
    if all_good:
        print("🎉 Структура проекта корректна!")
        return True
    else:
        print("⚠️ Найдены проблемы в структуре проекта")
        return False

if __name__ == '__main__':
    check_project_structure()