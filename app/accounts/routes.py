from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.accounts.models import (
    create_account, get_user_accounts, get_account_by_id,
    update_account, archive_account, restore_account
)
import json
import os

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

def load_banks():
    """Загрузка справочника банков"""
    try:
        with open('static/data/banks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"banks": []}

def load_currencies():
    """Загрузка справочника валют"""
    try:
        with open('static/data/currencies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"currencies": []}

@accounts_bp.route('/')
def accounts_list():
    """Страница списка счетов"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('accounts.html')

@accounts_bp.route('/create')
def create_account_page():
    """Страница создания счета"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    
    banks = load_banks()
    currencies = load_currencies()
    
    return render_template('create_account.html', 
                         banks=banks['banks'], 
                         currencies=currencies['currencies'])

@accounts_bp.route('/api/accounts', methods=['GET'])
def api_get_accounts():
    """API: Получение списка счетов пользователя"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    
    accounts = get_user_accounts(user_id, include_archived)
    return jsonify({'success': True, 'accounts': accounts})

@accounts_bp.route('/api/accounts', methods=['POST'])
def api_create_account():
    """API: Создание нового счета"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    # Валидация обязательных полей
    name = data.get('name', '').strip()
    account_type = data.get('type', '').strip()
    currency = data.get('currency', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Название счета обязательно'})
    if not account_type:
        return jsonify({'success': False, 'error': 'Тип счета обязателен'})
    if not currency:
        return jsonify({'success': False, 'error': 'Валюта обязательна'})
    
    # Валидация валюты
    currencies = load_currencies()
    valid_currencies = [c['code'] for c in currencies['currencies']]
    if currency not in valid_currencies:
        return jsonify({'success': False, 'error': 'Недопустимая валюта'})
    
    # Валидация банка (если указан)
    bank_id = data.get('bank_id', '').strip() or None
    if bank_id:
        banks = load_banks()
        valid_banks = [b['id'] for b in banks['banks']]
        if bank_id not in valid_banks:
            return jsonify({'success': False, 'error': 'Недопустимый банк'})
    
    # Валидация начального баланса
    try:
        initial_balance = float(data.get('initial_balance', 0))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Неверный формат начального баланса'})
    
    # Валидация типа счета
    valid_types = ['checking', 'savings', 'credit', 'deposit', 'investment', 'cash']
    if account_type not in valid_types:
        return jsonify({'success': False, 'error': 'Недопустимый тип счета'})
    
    # Создание счета
    success, result = create_account(
        user_id=user_id,
        name=name,
        account_type=account_type,
        currency=currency,
        bank_id=bank_id,
        initial_balance=initial_balance
    )
    
    if success:
        return jsonify({'success': True, 'account_id': result})
    else:
        return jsonify({'success': False, 'error': result})

@accounts_bp.route('/api/accounts/<int:account_id>', methods=['GET'])
def api_get_account(account_id):
    """API: Получение конкретного счета"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    account = get_account_by_id(account_id, user_id)
    
    if account:
        return jsonify({'success': True, 'account': account})
    else:
        return jsonify({'success': False, 'error': 'Счет не найден'}), 404

@accounts_bp.route('/api/accounts/<int:account_id>', methods=['PUT'])
def api_update_account(account_id):
    """API: Обновление счета"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    # Валидация данных
    name = data.get('name', '').strip() if data.get('name') else None
    account_type = data.get('type', '').strip() if data.get('type') else None
    currency = data.get('currency', '').strip() if data.get('currency') else None
    bank_id = data.get('bank_id', '').strip() if data.get('bank_id') else None
    
    # Валидация валюты (если указана)
    if currency:
        currencies = load_currencies()
        valid_currencies = [c['code'] for c in currencies['currencies']]
        if currency not in valid_currencies:
            return jsonify({'success': False, 'error': 'Недопустимая валюта'})
    
    # Валидация банка (если указан)
    if bank_id:
        banks = load_banks()
        valid_banks = [b['id'] for b in banks['banks']]
        if bank_id not in valid_banks:
            return jsonify({'success': False, 'error': 'Недопустимый банк'})
    
    # Валидация типа счета (если указан)
    if account_type:
        valid_types = ['checking', 'savings', 'credit', 'deposit', 'investment', 'cash']
        if account_type not in valid_types:
            return jsonify({'success': False, 'error': 'Недопустимый тип счета'})
    
    success, result = update_account(
        account_id=account_id,
        user_id=user_id,
        name=name,
        account_type=account_type,
        currency=currency,
        bank_id=bank_id
    )
    
    if success:
        return jsonify({'success': True, 'message': result})
    else:
        return jsonify({'success': False, 'error': result})

@accounts_bp.route('/api/accounts/<int:account_id>/archive', methods=['POST'])
def api_archive_account(account_id):
    """API: Архивирование счета"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    success, result = archive_account(account_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': result})
    else:
        return jsonify({'success': False, 'error': result})

@accounts_bp.route('/api/accounts/<int:account_id>/restore', methods=['POST'])
def api_restore_account(account_id):
    """API: Восстановление счета"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    user_id = session['user_id']
    success, result = restore_account(account_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': result})
    else:
        return jsonify({'success': False, 'error': result})

@accounts_bp.route('/api/data/banks', methods=['GET'])
def api_get_banks():
    """API: Получение справочника банков"""
    banks = load_banks()
    return jsonify(banks)

@accounts_bp.route('/api/data/currencies', methods=['GET'])
def api_get_currencies():
    """API: Получение справочника валют"""
    currencies = load_currencies()
    return jsonify(currencies)