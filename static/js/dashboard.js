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
}

function createBot() {
    // Implementar criação de bot
    console.log('Criar bot clicado');
    alert('Funcionalidade de criação de bot será implementada em breve!');
}

function editBot(botId) {
    // Implementar edição de bot
    console.log('Editar bot:', botId);
    alert('Funcionalidade de edição será implementada em breve!');
}

function deleteBot(botId) {
    // Implementar exclusão de bot
    if (confirm('Tem certeza que deseja excluir este bot?')) {
        console.log('Excluir bot:', botId);
        alert('Funcionalidade de exclusão será implementada em breve!');
    }
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
