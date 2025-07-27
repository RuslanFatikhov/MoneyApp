from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.auth.models import create_user, verify_user
from app.auth.validators import is_valid_email, is_valid_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login_page():
    return render_template('login.html')

@auth_bp.route('/register')
def register_page():
    return render_template('register.html')

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Валидация
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email и пароль обязательны'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'error': 'Неверный формат email'})
    
    valid_password, password_error = is_valid_password(password)
    if not valid_password:
        return jsonify({'success': False, 'error': password_error})
    
    # Создание пользователя
    success, result = create_user(email, password)
    if success:
        session['user_id'] = result
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result})

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email и пароль обязательны'})
    
    success, result = verify_user(email, password)
    if success:
        session['user_id'] = result
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result})

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'success': True})