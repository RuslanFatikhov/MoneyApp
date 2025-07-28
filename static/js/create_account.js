document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('create-account-form');
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');
    const bankSelect = document.getElementById('bank_id');
    const nameInput = document.getElementById('name');

    // Автозаполнение названия при выборе банка
    bankSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const bankName = selectedOption.text;
        const typeSelect = document.getElementById('type');
        const selectedType = typeSelect.options[typeSelect.selectedIndex];
        
        if (bankName && bankName !== 'Выберите банк' && !nameInput.value.trim()) {
            let accountTypeName = '';
            if (selectedType && selectedType.value) {
                const typeNames = {
                    'checking': 'Расчетный',
                    'savings': 'Сберегательный', 
                    'credit': 'Кредитная карта',
                    'deposit': 'Депозит',
                    'investment': 'Инвестиционный',
                    'cash': 'Наличные'
                };
                accountTypeName = typeNames[selectedType.value] || '';
            }
            
            if (accountTypeName) {
                nameInput.value = `${accountTypeName} ${bankName}`;
            } else {
                nameInput.value = `Счет ${bankName}`;
            }
        }
    });

    // Автозаполнение названия при выборе типа счета
    document.getElementById('type').addEventListener('change', function() {
        const selectedBank = bankSelect.options[bankSelect.selectedIndex];
        const bankName = selectedBank.text;
        const selectedType = this.options[this.selectedIndex];
        
        if (selectedType.value && bankName && bankName !== 'Выберите банк' && !nameInput.value.trim()) {
            const typeNames = {
                'checking': 'Расчетный',
                'savings': 'Сберегательный', 
                'credit': 'Кредитная карта',
                'deposit': 'Депозит',
                'investment': 'Инвестиционный',
                'cash': 'Наличные'
            };
            const accountTypeName = typeNames[selectedType.value] || selectedType.text;
            nameInput.value = `${accountTypeName} ${bankName}`;
        }
    });

    // Обработка отправки формы
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            name: formData.get('name').trim(),
            type: formData.get('type'),
            currency: formData.get('currency'),
            bank_id: formData.get('bank_id') || null,
            initial_balance: parseFloat(formData.get('initial_balance')) || 0
        };
        
        clearMessages();
        setFormLoading(true);
        
        try {
            const response = await fetch('/accounts/api/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showSuccess('Счет успешно создан! Перенаправление...');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showError(result.error);
                setFormLoading(false);
            }
        } catch (error) {
            showError('Ошибка соединения с сервером');
            setFormLoading(false);
        }
    });

    function showError(message) {
        errorDiv.textContent = 'Ошибка: ' + message;
        errorDiv.style.display = 'block';
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function showSuccess(message) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function clearMessages() {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }

    function setFormLoading(loading) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (loading) {
            submitBtn.textContent = 'Создание...';
            submitBtn.disabled = true;
            form.classList.add('loading');
        } else {
            submitBtn.textContent = 'Создать счет';
            submitBtn.disabled = false;
            form.classList.remove('loading');
        }
    }
});