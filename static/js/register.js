document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        clearMessages();
        
        try {
            const response = await fetch('/auth/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess('Регистрация успешна! Перенаправление...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Ошибка соединения');
        }
    });

    function showError(message) {
        errorDiv.textContent = 'Ошибка: ' + message;
        errorDiv.style.display = 'block';
    }

    function showSuccess(message) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }

    function clearMessages() {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }
});