// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Carregar estatísticas
    loadStats();
    
    // Carregar bots
    loadBots();
    
    // Configurar eventos
    setupEventListeners();
});

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('total-bots').textContent = stats.total_bots;
        document.getElementById('active-bots').textContent = stats.active_bots;
        document.getElementById('total-messages').textContent = stats.total_messages;
        document.getElementById('uptime').textContent = stats.uptime;
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function loadBots() {
    try {
        const response = await fetch('/api/bots');
        const bots = await response.json();
        
        const botsList = document.getElementById('bots-list');
        
        if (bots.length === 0) {
            botsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <h3>Nenhum bot criado ainda</h3>
                    <p>Crie seu primeiro bot para começar a gerenciar mensagens automaticamente</p>
                    <button class="btn-primary" onclick="createBot()">Criar Primeiro Bot</button>
                </div>
            `;
        } else {
            botsList.innerHTML = bots.map(bot => `
                <div class="bot-card">
                    <div class="bot-info">
                        <div class="bot-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="bot-details">
                            <h3>${bot.name}</h3>
                            <p>${bot.description || 'Sem descrição'}</p>
                        </div>
                    </div>
                    <div class="bot-status ${bot.status}">
                        <span>${bot.status}</span>
                    </div>
                    <div class="bot-actions">
                        <button class="btn-icon" onclick="editBot('${bot.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon" onclick="deleteBot('${bot.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar bots:', error);
    }
}

function setupEventListeners() {
    // Navegação
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover active de todos
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            
            // Adicionar active ao clicado
            this.classList.add('active');
        });
    });
    
    // Botões de ação rápida
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const text = this.querySelector('span').textContent;
            console.log('Ação clicada:', text);
            
            // Adicionar feedback visual
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Form de criação de bot
    document.getElementById('createBotForm').addEventListener('submit', function(e) {
        e.preventDefault();
        createBot();
    });
    
    // Fechar modais ao clicar fora
    window.addEventListener('click', function(e) {
        const createModal = document.getElementById('createBotModal');
        const confirmModal = document.getElementById('confirmModal');
        const accountsModal = document.getElementById('accountsModal');
        const addAccountModal = document.getElementById('addAccountModal');
        
        if (e.target === createModal) {
            closeCreateBotModal();
        }
        if (e.target === confirmModal) {
            closeConfirmModal();
        }
        if (e.target === accountsModal) {
            closeAccountsModal();
        }
        if (e.target === addAccountModal) {
            closeAddAccountModal();
        }
    });
    
    // Event listener para formulário de adicionar conta
    document.getElementById('addAccountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addAccount();
    });
}

// Modal Functions
function openCreateBotModal() {
    document.getElementById('createBotModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeCreateBotModal() {
    document.getElementById('createBotModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('createBotForm').reset();
}

function openConfirmModal(message, callback) {
    document.getElementById('confirmMessage').textContent = message;
    document.getElementById('confirmButton').onclick = callback;
    document.getElementById('confirmModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeConfirmModal() {
    document.getElementById('confirmModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Account Modal Functions
function openAccountsModal() {
    document.getElementById('accountsModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    loadAccounts();
}

function closeAccountsModal() {
    document.getElementById('accountsModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function openAddAccountModal() {
    document.getElementById('addAccountModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAddAccountModal() {
    document.getElementById('addAccountModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('addAccountForm').reset();
}

// Bot Management Functions
async function createBot() {
    const form = document.getElementById('createBotForm');
    const formData = new FormData(form);
    
    const botData = {
        name: formData.get('name'),
        description: formData.get('description'),
        bot_type: formData.get('bot_type'),
        token: formData.get('token'),
        api_id: formData.get('api_id'),
        api_hash: formData.get('api_hash'),
        phone_number: formData.get('phone_number'),
        config: {}
    };
    
    try {
        const response = await fetch('/api/bots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(botData)
        });
        
        if (response.ok) {
            const newBot = await response.json();
            console.log('Bot criado:', newBot);
            
            // Fechar modal e recarregar lista
            closeCreateBotModal();
            loadBots();
            loadStats();
            
            // Mostrar sucesso
            showNotification('Bot criado com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(`Erro: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao criar bot:', error);
        showNotification('Erro ao criar bot. Tente novamente.', 'error');
    }
}

async function editBot(botId) {
    try {
        const response = await fetch(`/api/bots/${botId}`);
        if (response.ok) {
            const bot = await response.json();
            console.log('Editar bot:', bot);
            showNotification('Funcionalidade de edição será implementada em breve!', 'info');
        } else {
            showNotification('Erro ao carregar dados do bot', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar bot:', error);
        showNotification('Erro ao carregar dados do bot', 'error');
    }
}

async function deleteBot(botId) {
    openConfirmModal('Tem certeza que deseja excluir este bot? Esta ação não pode ser desfeita.', async () => {
        try {
            const response = await fetch(`/api/bots/${botId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                closeConfirmModal();
                loadBots();
                loadStats();
                showNotification('Bot excluído com sucesso!', 'success');
            } else {
                const error = await response.json();
                showNotification(`Erro: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Erro ao excluir bot:', error);
            showNotification('Erro ao excluir bot. Tente novamente.', 'error');
        }
    });
}

async function startBot(botId) {
    try {
        const response = await fetch(`/api/bots/${botId}/start`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadBots();
            loadStats();
            showNotification('Bot iniciado com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(`Erro: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao iniciar bot:', error);
        showNotification('Erro ao iniciar bot. Tente novamente.', 'error');
    }
}

async function stopBot(botId) {
    try {
        const response = await fetch(`/api/bots/${botId}/stop`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadBots();
            loadStats();
            showNotification('Bot parado com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(`Erro: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao parar bot:', error);
        showNotification('Erro ao parar bot. Tente novamente.', 'error');
    }
}

// Notification System
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Adicionar ao body
    document.body.appendChild(notification);
    
    // Mostrar notificação
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Remover após 5 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Account Management Functions
async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        if (response.ok) {
            const accounts = await response.json();
            displayAccounts(accounts);
        } else {
            console.error('Erro ao carregar contas');
        }
    } catch (error) {
        console.error('Erro ao carregar contas:', error);
    }
}

function displayAccounts(accounts) {
    const accountsList = document.getElementById('accountsList');
    
    if (accounts.length === 0) {
        accountsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-plus"></i>
                <h3>Nenhuma conta adicionada</h3>
                <p>Adicione suas contas do Telegram para gerenciar bots</p>
            </div>
        `;
    } else {
        accountsList.innerHTML = accounts.map(account => `
            <div class="account-card">
                <div class="account-info">
                    <div class="account-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="account-details">
                        <h3>${account.phone_number}</h3>
                        <p>API ID: ${account.api_id}</p>
                    </div>
                </div>
                <div class="account-status ${account.is_authenticated ? 'authenticated' : 'pending'}">
                    <span>${account.is_authenticated ? 'Autenticado' : 'Pendente'}</span>
                </div>
                <div class="account-actions">
                    <button class="btn-icon" onclick="testAccountConnection(${account.id})">
                        <i class="fas fa-wifi"></i>
                    </button>
                    <button class="btn-icon" onclick="deleteAccount(${account.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

async function addAccount() {
    const form = document.getElementById('addAccountForm');
    const formData = new FormData(form);
    
    const accountData = {
        phone_number: formData.get('phone_number'),
        api_id: formData.get('api_id'),
        api_hash: formData.get('api_hash')
    };
    
    try {
        const response = await fetch('/api/accounts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(accountData)
        });
        
        if (response.ok) {
            const newAccount = await response.json();
            showNotification('Conta adicionada com sucesso!', 'success');
            closeAddAccountModal();
            loadAccounts();
        } else {
            const error = await response.json();
            showNotification(`Erro: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao adicionar conta:', error);
        showNotification('Erro ao adicionar conta: ' + error.message, 'error');
    }
}

async function testAccountConnection(accountId) {
    try {
        const response = await fetch(`/api/accounts/${accountId}/test-connection`);
        if (response.ok) {
            const result = await response.json();
            showNotification(result.message, result.success ? 'success' : 'error');
        } else {
            showNotification('Erro ao testar conexão', 'error');
        }
    } catch (error) {
        console.error('Erro ao testar conexão:', error);
        showNotification('Erro ao testar conexão', 'error');
    }
}

async function deleteAccount(accountId) {
    openConfirmModal('Tem certeza que deseja deletar esta conta?', async () => {
        try {
            const response = await fetch(`/api/accounts/${accountId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showNotification('Conta deletada com sucesso!', 'success');
                loadAccounts();
            } else {
                showNotification('Erro ao deletar conta', 'error');
            }
        } catch (error) {
            console.error('Erro ao deletar conta:', error);
            showNotification('Erro ao deletar conta', 'error');
        }
        closeConfirmModal();
    });
}

// Utility Functions
function toggleFilter() {
    showNotification('Funcionalidade de filtro será implementada em breve!', 'info');
}

function toggleSort() {
    showNotification('Funcionalidade de ordenação será implementada em breve!', 'info');
}

// Animações de entrada
function animateOnScroll() {
    const elements = document.querySelectorAll('.stat-card, .action-btn, .bots-section');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

// Inicializar animações
window.addEventListener('scroll', animateOnScroll);
animateOnScroll();
