document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    const accountsSummary = document.getElementById('accounts-summary');
    const recentTransactions = document.getElementById('recent-transactions');
    const totalBalance = document.getElementById('total-balance');
    const balanceBreakdown = document.getElementById('balance-breakdown');

    // Загрузка данных при старте
    loadDashboardData();

    // Обработчик выхода
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

    async function loadDashboardData() {
        await Promise.all([
            loadAccountsSummary(),
            loadRecentTransactions(),
            loadTotalBalance()
        ]);
    }

    async function loadAccountsSummary() {
        try {
            const response = await fetch('/accounts/api/accounts');
            const data = await response.json();
            
            if (data.success && data.accounts.length > 0) {
                const banksResponse = await fetch('/accounts/api/data/banks');
                const banksData = await banksResponse.json();
                const banks = banksData.banks || [];
                
                renderAccountsSummary(data.accounts, banks);
            } else {
                accountsSummary.innerHTML = `
                    <div class="no-data">
                        <p>У вас пока нет счетов</p>
                        <a href="/accounts/create" class="btn-primary">Создать первый счет</a>
                    </div>
                `;
            }
        } catch (error) {
            accountsSummary.innerHTML = '<div class="loading-text">Ошибка загрузки счетов</div>';
        }
    }

    async function loadRecentTransactions() {
        try {
            // Пока транзакций нет, показываем заглушку
            recentTransactions.innerHTML = `
                <div class="no-data">
                    Транзакции появятся после загрузки выписок
                </div>
            `;
        } catch (error) {
            recentTransactions.innerHTML = '<div class="loading-text">Ошибка загрузки транзакций</div>';
        }
    }

    async function loadTotalBalance() {
        try {
            const response = await fetch('/accounts/api/accounts');
            const data = await response.json();
            
            if (data.success && data.accounts.length > 0) {
                calculateAndDisplayTotalBalance(data.accounts);
            } else {
                totalBalance.innerHTML = `
                    <div class="no-data">
                        Создайте счета для отображения баланса
                    </div>
                `;
            }
        } catch (error) {
            totalBalance.innerHTML = '<div class="loading-text">Ошибка подсчета баланса</div>';
        }
    }

    function renderAccountsSummary(accounts, banks) {
        // Показываем только первые 3 счета
        const displayAccounts = accounts.slice(0, 3);
        
        const html = displayAccounts.map(account => {
            const bank = banks.find(b => b.id === account.bank_id);
            const bankColor = bank ? bank.color : '#9E9E9E';
            const isNegative = account.current_balance < 0;
            
            return `

                
                <div class="account-summary-item">
                    <div class="account-info">
                        <div class="account-bank-dot" style="background-color: ${bankColor}"></div>
                        <span class="account-name">${escapeHtml(account.name)}</span>
                    </div>
                    <div class="account-balance ${isNegative ? 'negative' : ''}">
                        ${formatCurrency(account.current_balance, account.currency)}
                    </div>
                </div>
            `;
        }).join('');
        
        accountsSummary.innerHTML = html;
        
        // Добавляем ссылку "Показать все" если счетов больше 3
        if (accounts.length > 3) {
            accountsSummary.innerHTML += `
                <div style="text-align: center; margin-top: 15px;">
                    <a href="/accounts" class="btn-secondary">Показать все (${accounts.length})</a>
                </div>
            `;
        }
    }

    function calculateAndDisplayTotalBalance(accounts) {
        // Группируем по валютам
        const balancesByCurrency = {};
        
        accounts.forEach(account => {
            if (!account.archived) {
                if (!balancesByCurrency[account.currency]) {
                    balancesByCurrency[account.currency] = 0;
                }
                balancesByCurrency[account.currency] += account.current_balance;
            }
        });
        
        const currencies = Object.keys(balancesByCurrency);
        
        if (currencies.length === 0) {
            totalBalance.innerHTML = '<div class="no-data">Нет активных счетов</div>';
            return;
        }
        
        // Если одна валюта - показываем как основной баланс
        if (currencies.length === 1) {
            const currency = currencies[0];
            const amount = balancesByCurrency[currency];
            
            totalBalance.innerHTML = `
                <div class="balance-amount ${amount < 0 ? 'negative' : ''}">
                    ${formatCurrency(amount, currency)}
                </div>
            `;
        } else {
            // Если несколько валют - показываем как мультивалютный
            totalBalance.innerHTML = `
                <div class="balance-amount mixed">
                    Мультивалютный
                </div>
            `;
            
            const breakdownHtml = currencies.map(currency => {
                const amount = balancesByCurrency[currency];
                return `
                    <div class="currency-balance">
                        <span class="currency-code">${currency}</span>
                        <span class="currency-amount ${amount < 0 ? 'negative' : ''}">
                            ${formatCurrency(amount, currency)}
                        </span>
                    </div>
                `;
            }).join('');
            
            balanceBreakdown.innerHTML = breakdownHtml;
        }
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