document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    const accountsSummary = document.getElementById('accounts-summary');
    const totalValueAmount = document.getElementById('total-value-amount');
    const currencyBtn = document.getElementById('currency-btn');
    const currencySymbol = document.getElementById('currency-symbol');
    const currencyDropdown = document.getElementById('currency-dropdown');
    const currencyList = document.getElementById('currency-list');
    const currencySearch = document.getElementById('currency-search');

    // Данные
    let accounts = [];
    let currencies = [];
    let exchangeRates = {};
    let selectedCurrency = getCurrencyFromCookie() || 'USD';

    // Загрузка данных при старте
    loadDashboardData();

    // Обработчик выхода
    if (logoutBtn) {
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
    }

    // Обработчики для валютного селектора
    currencyBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleCurrencyDropdown();
    });

    currencySearch.addEventListener('input', function() {
        filterCurrencies(this.value);
    });

    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function() {
        hideCurrencyDropdown();
    });

    currencyDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    async function loadDashboardData() {
        await Promise.all([
            loadCurrencies(),
            loadExchangeRates(),
            loadAccountsData()
        ]);
        
        updateTotalValue();
        loadAccountsSummary();
    }

    async function loadCurrencies() {
        try {
            const response = await fetch('/static/data/currencies.json');
            const data = await response.json();
            currencies = data.currencies || [];
            renderCurrencyList();
            updateCurrencySymbol();
        } catch (error) {
            console.error('Ошибка загрузки валют:', error);
            currencyList.innerHTML = '<div class="error-text">Ошибка загрузки валют</div>';
        }
    }

    async function loadExchangeRates() {
        try {
            // Используем бесплатный API exchangerate-api.com
            const response = await fetch(`https://api.exchangerate-api.com/v4/latest/USD`);
            const data = await response.json();
            exchangeRates = data.rates || {};
            exchangeRates['USD'] = 1; // USD как базовая валюта
        } catch (error) {
            console.error('Ошибка загрузки курсов валют:', error);
            // Фоллбек - устанавливаем базовые курсы
            exchangeRates = {
                'USD': 1,
                'EUR': 0.85,
                'KZT': 450,
                'RUB': 90,
                'CNY': 7.2,
                'GBP': 0.73,
                'JPY': 150
            };
        }
    }

    async function loadAccountsData() {
        try {
            const response = await fetch('/accounts/api/accounts');
            const data = await response.json();
            
            if (data.success) {
                accounts = data.accounts || [];
            }
        } catch (error) {
            console.error('Ошибка загрузки счетов:', error);
            accounts = [];
        }
    }

    async function loadAccountsSummary() {
        try {
            if (accounts.length > 0) {
                const banksResponse = await fetch('/static/data/banks.json');
                const banksData = await banksResponse.json();
                const banks = banksData.banks || [];
                
                renderAccountsSummary(accounts, banks);
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

    function updateTotalValue() {
        if (accounts.length === 0) {
            totalValueAmount.innerHTML = `
                <div class="no-data">
                    Создайте счета для отображения общей стоимости
                </div>
            `;
            return;
        }

        // Подсчитываем общую стоимость в USD
        let totalInUSD = 0;
        
        accounts.forEach(account => {
            if (!account.archived) {
                const accountBalance = account.current_balance || 0;
                const accountCurrency = account.currency;
                
                // Конвертируем в USD
                if (accountCurrency === 'USD') {
                    totalInUSD += accountBalance;
                } else if (exchangeRates[accountCurrency]) {
                    totalInUSD += accountBalance / exchangeRates[accountCurrency];
                }
            }
        });

        // Конвертируем из USD в выбранную валюту
        let totalInSelectedCurrency = totalInUSD;
        if (selectedCurrency !== 'USD' && exchangeRates[selectedCurrency]) {
            totalInSelectedCurrency = totalInUSD * exchangeRates[selectedCurrency];
        }

        // Отображаем результат
        const isNegative = totalInSelectedCurrency < 0;
        const formattedAmount = formatCurrencyValue(Math.abs(totalInSelectedCurrency));
        
        totalValueAmount.innerHTML = `
            <h1 class="total-amount primary1 fw700 ${isNegative ? 'negative' : ''}">
                ${isNegative ? '-' : ''}${formattedAmount}
            </h1>
        `;
    }

    function renderCurrencyList() {
        const html = currencies.map(currency => `
            <div class="currency-item" data-currency="${currency.code}">
                <span class="currency-symbol">${currency.symbol}</span>
                <span class="currency-code">${currency.code}</span>
                <span class="currency-name">${currency.name}</span>
            </div>
        `).join('');
        
        currencyList.innerHTML = html;
        
        // Добавляем обработчики клика
        currencyList.querySelectorAll('.currency-item').forEach(item => {
            item.addEventListener('click', function() {
                const currency = this.dataset.currency;
                selectCurrency(currency);
            });
        });
    }

    function filterCurrencies(searchText) {
        const items = currencyList.querySelectorAll('.currency-item');
        const search = searchText.toLowerCase();
        
        items.forEach(item => {
            const code = item.querySelector('.currency-code').textContent.toLowerCase();
            const name = item.querySelector('.currency-name').textContent.toLowerCase();
            
            if (code.includes(search) || name.includes(search)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    function selectCurrency(currencyCode) {
        selectedCurrency = currencyCode;
        setCurrencyToCookie(currencyCode);
        updateCurrencySymbol();
        updateTotalValue();
        hideCurrencyDropdown();
        currencySearch.value = '';
        filterCurrencies(''); // Показать все валюты
    }

    function updateCurrencySymbol() {
        const currency = currencies.find(c => c.code === selectedCurrency);
        if (currency) {
            currencySymbol.textContent = currency.symbol;
            currencyBtn.title = `Текущая валюта: ${currency.name}`;
        }
    }

    function toggleCurrencyDropdown() {
        currencyDropdown.classList.toggle('hidden');
        if (!currencyDropdown.classList.contains('hidden')) {
            currencySearch.focus();
        }
    }

    function hideCurrencyDropdown() {
        currencyDropdown.classList.add('hidden');
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

    function formatCurrency(amount, currency) {
        const currencyObj = currencies.find(c => c.code === currency);
        const symbol = currencyObj ? currencyObj.symbol : currency;
        
        const formattedAmount = new Intl.NumberFormat('ru-RU', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
        
        return `${symbol}${formattedAmount}`;
    }

    function formatCurrencyValue(amount) {
        return new Intl.NumberFormat('ru-RU', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Работа с cookies
    function setCurrencyToCookie(currency) {
        const expires = new Date();
        expires.setFullYear(expires.getFullYear() + 1); // Храним год
        document.cookie = `preferred_currency=${currency}; expires=${expires.toUTCString()}; path=/`;
    }

    function getCurrencyFromCookie() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'preferred_currency') {
                return value;
            }
        }
        return null;
    }
});