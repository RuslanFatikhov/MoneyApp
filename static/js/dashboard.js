document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');

    logoutBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/auth/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Ошибка выхода:', error);
        }
    });
});