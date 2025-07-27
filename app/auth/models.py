import sqlite3
import bcrypt
from datetime import datetime

def get_db():
    conn = sqlite3.connect('database/finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email, password):
    conn = get_db()
    try:
        # Проверка существования email
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            return False, "Email уже зарегистрирован"
        
        # Хеширование пароля
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Создание пользователя
        cursor = conn.execute(
            'INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)',
            (email, password_hash, datetime.now())
        )
        conn.commit()
        return True, cursor.lastrowid
    except Exception as e:
        return False, f"Ошибка создания пользователя: {str(e)}"
    finally:
        conn.close()

def verify_user(email, password):
    conn = get_db()
    try:
        user = conn.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            return False, "Неверный email или пароль"
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return True, user['id']
        else:
            return False, "Неверный email или пароль"
    except Exception as e:
        return False, f"Ошибка входа: {str(e)}"
    finally:
        conn.close()