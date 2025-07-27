import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    if not re.search(r'[A-Za-z]', password):
        return False, "Пароль должен содержать буквы"
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифры"
    return True, ""