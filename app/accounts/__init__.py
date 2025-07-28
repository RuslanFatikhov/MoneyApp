import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple

def get_db():
    conn = sqlite3.connect('database/finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_account(user_id: int, name: str, account_type: str, currency: str, 
                  bank_id: str = None, initial_balance: float = 0.0) -> Tuple[bool, str]:
    """Создание нового счета"""
    conn = get_db()
    try:
        cursor = conn.execute(
            '''INSERT INTO accounts (user_id, name, type, currency, bank_id, 
               initial_balance, archived, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, 0, ?)''',
            (user_id, name, account_type, currency, bank_id, initial_balance, datetime.now())
        )
        conn.commit()
        return True, str(cursor.lastrowid)
    except Exception as e:
        return False, f"Ошибка создания счета: {str(e)}"
    finally:
        conn.close()

def get_user_accounts(user_id: int, include_archived: bool = False) -> List[Dict]:
    """Получение всех счетов пользователя"""
    conn = get_db()
    try:
        query = '''SELECT id, name, type, currency, bank_id, initial_balance, 
                   archived, created_at FROM accounts WHERE user_id = ?'''
        params = [user_id]
        
        if not include_archived:
            query += ' AND archived = 0'
        
        query += ' ORDER BY created_at DESC'
        
        accounts = conn.execute(query, params).fetchall()
        
        result = []
        for account in accounts:
            # Вычисляем текущий баланс
            balance_query = '''SELECT SUM(amount) as total FROM transactions 
                              WHERE account_id = ? AND status = "confirmed"'''
            balance_result = conn.execute(balance_query, (account['id'],)).fetchone()
            current_balance = account['initial_balance'] + (balance_result['total'] or 0)
            
            result.append({
                'id': account['id'],
                'name': account['name'],
                'type': account['type'],
                'currency': account['currency'],
                'bank_id': account['bank_id'],
                'initial_balance': account['initial_balance'],
                'current_balance': current_balance,
                'archived': bool(account['archived']),
                'created_at': account['created_at']
            })
        
        return result
    except Exception as e:
        print(f"Ошибка получения счетов: {e}")
        return []
    finally:
        conn.close()

def get_account_by_id(account_id: int, user_id: int) -> Optional[Dict]:
    """Получение конкретного счета пользователя"""
    conn = get_db()
    try:
        account = conn.execute(
            '''SELECT id, name, type, currency, bank_id, initial_balance, 
               archived, created_at FROM accounts 
               WHERE id = ? AND user_id = ?''',
            (account_id, user_id)
        ).fetchone()
        
        if not account:
            return None
        
        # Вычисляем текущий баланс
        balance_query = '''SELECT SUM(amount) as total FROM transactions 
                          WHERE account_id = ? AND status = "confirmed"'''
        balance_result = conn.execute(balance_query, (account_id,)).fetchone()
        current_balance = account['initial_balance'] + (balance_result['total'] or 0)
        
        return {
            'id': account['id'],
            'name': account['name'],
            'type': account['type'],
            'currency': account['currency'],
            'bank_id': account['bank_id'],
            'initial_balance': account['initial_balance'],
            'current_balance': current_balance,
            'archived': bool(account['archived']),
            'created_at': account['created_at']
        }
    except Exception as e:
        print(f"Ошибка получения счета: {e}")
        return None
    finally:
        conn.close()

def update_account(account_id: int, user_id: int, name: str = None, 
                  account_type: str = None, currency: str = None,
                  bank_id: str = None) -> Tuple[bool, str]:
    """Обновление данных счета"""
    conn = get_db()
    try:
        # Проверяем что счет принадлежит пользователю
        existing = conn.execute(
            'SELECT id FROM accounts WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        ).fetchone()
        
        if not existing:
            return False, "Счет не найден"
        
        # Формируем запрос обновления
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if account_type is not None:
            updates.append("type = ?")
            params.append(account_type)
        if currency is not None:
            updates.append("currency = ?")
            params.append(currency)
        if bank_id is not None:
            updates.append("bank_id = ?")
            params.append(bank_id)
        
        if not updates:
            return False, "Нет данных для обновления"
        
        params.extend([account_id, user_id])
        query = f"UPDATE accounts SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        
        conn.execute(query, params)
        conn.commit()
        return True, "Счет обновлен"
    except Exception as e:
        return False, f"Ошибка обновления счета: {str(e)}"
    finally:
        conn.close()

def archive_account(account_id: int, user_id: int) -> Tuple[bool, str]:
    """Архивирование счета (мягкое удаление)"""
    conn = get_db()
    try:
        # Проверяем что счет принадлежит пользователю
        existing = conn.execute(
            'SELECT id FROM accounts WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        ).fetchone()
        
        if not existing:
            return False, "Счет не найден"
        
        conn.execute(
            'UPDATE accounts SET archived = 1 WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        )
        conn.commit()
        return True, "Счет архивирован"
    except Exception as e:
        return False, f"Ошибка архивирования: {str(e)}"
    finally:
        conn.close()

def restore_account(account_id: int, user_id: int) -> Tuple[bool, str]:
    """Восстановление архивированного счета"""
    conn = get_db()
    try:
        # Проверяем что счет принадлежит пользователю
        existing = conn.execute(
            'SELECT id FROM accounts WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        ).fetchone()
        
        if not existing:
            return False, "Счет не найден"
        
        conn.execute(
            'UPDATE accounts SET archived = 0 WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        )
        conn.commit()
        return True, "Счет восстановлен"
    except Exception as e:
        return False, f"Ошибка восстановления: {str(e)}"
    finally:
        conn.close()