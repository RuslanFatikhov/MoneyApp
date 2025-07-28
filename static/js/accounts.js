document.addEventListener('DOMContentLoaded', function() {
    const accountsList = document.getElementById('accounts-list');
    const loadingSpinner = document.getElementById('accounts-loading');
    const noAccountsDiv = document.getElementById('no-accounts');
    const toggleArchivedBtn = document.getElementById('toggle-archived-btn');
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-account-form');
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');

    let showArchived = false;
    let accounts = [];
    let banks = [];

    // Загрузка данных при старте
    loadAccounts();
    loadBanks();

    // Обработчики событий
    toggleArchivedBtn.addEventListener('click', toggleArchivedAccounts);
    editForm.addEventListener('submit', handleEditSubmit);
    
    // Закрытие модального окна
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeEditModal);
    });
    
    editModal.addEventListener('click', function(e) {
        if (e.target === editModal) {
            closeEditModal();
        }
    });

    async function loadAccounts() {
        showLoading(true);
        
        try {
            const response = await fetch(`/accounts/api/accounts?include_archived=${showArchived}`);
            const data = await response.json();
            
            if (data.success) {
                accounts = data.accounts;
                renderAccounts();
            } else {
                showError('Ошибка загрузки счетов');
            }
        } catch (error) {
            showError('Ошибка соединения с сервером');
        } finally {
            showLoading(false);
        }
    }

    async function loadBanks() {
        try {
            const response = await fetch('/accounts/api/data/banks');
            const data = await response.json();
            banks = data.banks || [];
            populateBankSelect();
        } catch (error) {
            console.error('Ошибка загрузки банков:', error);
        }
    }

    function populateBankSelect() {
        const bankSelect = document.getElementById('edit-bank');
        bankSelect.innerHTML = '<option value="">Выберите банк</option>';
        
        banks.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank.id;
            option.textContent = bank.name;
            bankSelect.appendChild(option);
        });
    }

    function renderAccounts() {
        if (accounts.length === 0) {
            accountsList.style.display = 'none';
            noAccountsDiv.style.display = 'block';
            return;
        }

        accountsList.style.display = 'grid';
        noAccountsDiv.style.display = 'none';
        
        accountsList.innerHTML = accounts.map(account => {
            const bank = banks.find(b => b.id === account.bank_id);
            const bankColor = bank ? bank.color : '#9E9E9E';
            const bankName = bank ? bank.name : 'Не указан';
            
            const typeNames = {
                'checking': 'Расчетный счет',
                'savings': 'Сберегательный',
                'credit': 'Кредитная карта',
                'deposit': 'Депозит',
                'investment': 'Инвестиционный',
                'cash': 'Наличные'
            };

            const isNegative = account.current_balance < 0;
            const balanceClass = isNegative ? 'account-balance negative' : 'account-balance';
            
            return `
                <div class="account-card ${account.archived ? 'archived' : ''}" data-account-id="${account.id}">
                    <div class="account-header">
                        <h3 class="account-name">${escapeHtml(account.name)}</h3>
                        <div class="bank-indicator" style="background-color: ${bankColor}" title="${bankName}"></div>
                    </div>
                    
                    <div class="account-type">${typeNames[account.type] || account.type}</div>
                    
                    <div class="${balanceClass}">
                        ${formatCurrency(account.current_balance, account.currency)}
                    </div>
                    
                    <div class="account-currency">
                        Банк: ${bankName} | Валюта: ${account.currency}
                    </div>
                    
                    <div class="account-actions">
                        <button class="btn-edit" onclick="editAccount(${account.id})">
                            Изменить
                        </button>
                        <button class="btn-transactions" onclick="viewTransactions(${account.id})">
                            Транзакции
                        </button>
                        ${account.archived ? 
                            `<button class="btn-restore" onclick="restoreAccount(${account.id})">Восстановить</button>` :
                            `<button class="btn-archive" onclick="archiveAccount(${account.id})">Архивировать</button>`
                        }
                    </div>
                </div>
            `;
        }).join('');
    }

    function toggleArchivedAccounts() {
        showArchived = !showArchived;
        toggleArchivedBtn.textContent = showArchived ? 'Скрыть архивированные' : 'Показать архивированные';
        loadAccounts();
    }

    // Глобальные функции для обработчиков событий
    window.editAccount = function(accountId) {
        const account = accounts.find(a => a.id === accountId);
        if (!account) return;

        document.getElementById('edit-account-id').value = account.id;
        document.getElementById('edit-name').value = account.name;
        document.getElementById('edit-type').value = account.type;
        document.getElementById('edit-bank').value = account.bank_id || '';
        
        editModal.style.display = 'flex';
    };

    window.viewTransactions = function(accountId) {
        window.location.href = `/transactions?account_id=${accountId}`;
    };

    window.archiveAccount = async function(accountId) {
        if (!confirm('Вы уверены, что хотите архивировать этот счет?')) return;

        try {
            const response = await fetch(`/accounts/api/accounts/${accountId}/archive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess('Счет архивирован');
                loadAccounts();
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Ошибка архивирования счета');
        }
    };

    window.restoreAccount = async function(accountId) {
        try {
            const response = await fetch(`/accounts/api/accounts/${accountId}/restore`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess('Счет восстановлен');
                loadAccounts();
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('Ошибка восстановления счета');
        }
    };

    async function handleEditSubmit(e) {
        e.preventDefault();
        
        const accountId = document.getElementById('edit-account-id').value;
        const data = {
            name: document.getElementById('edit-name').value.trim(),
            type: document.getElementById('edit-type').value,
            bank_id: document.getElementById('edit-bank').value || null
        };

        try {
            const response = await fetch(`/accounts/api/accounts/${accountId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showSuccess('Счет обновлен');
                closeEditModal();
                loadAccounts();
            } else {
                showError(result.error);
            }
        } catch (error) {
            showError('Ошибка обновления счета');
        }
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        clearMessages();
    }

    function showLoading(loading) {
        if (loading) {
            loadingSpinner.style.display = 'block';
            accountsList.style.display = 'none';
            noAccountsDiv.style.display = 'none';
        } else {
            loadingSpinner.style.display = 'none';
        }
    }

    function showError(message) {
        errorDiv.textContent = 'Ошибка: ' + message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    function showSuccess(message) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }

    function clearMessages() {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }

    function formatCurrency(amount, currency) {
        const symbols = {
            'KZT': '₸',
            'USD': '$',
            'EUR': '€',
            'RUB': '₽',
            'CNY': '¥',
            'GBP': '£',
            'JPY': '¥',
            'CHF': '₣',
            'CAD': 'C$',
            'AUD': 'A$'
        };
        
        const symbol = symbols[currency] || currency;
        const formattedAmount = new Intl.NumberFormat('ru-RU', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(Math.abs(amount));
        
        return amount < 0 ? `-${symbol}${formattedAmount}` : `${symbol}${formattedAmount}`;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});