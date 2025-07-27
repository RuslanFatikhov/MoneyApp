import sqlite3
import os

def init_database():
    # Создаём папку для БД если её нет
    os.makedirs('database', exist_ok=True)
    
    # Подключение к БД
    conn = sqlite3.connect('database/finance.db')
    
    # Читаем и выполняем схему
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print("✅ База данных инициализирована успешно!")

if __name__ == '__main__':
    init_database()