# 🤖 Telegram Bots Manager

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://github.com/seu-usuario/telegram-bots-manager/releases)
[![Downloads](https://img.shields.io/badge/Downloads-1k+-green.svg)](https://github.com/seu-usuario/telegram-bots-manager)

> **Sistema completo para gerenciar múltiplos bots do Telegram com interface web moderna, monitoramento em tempo real e funcionalidades avançadas.**

[![Deploy with Portainer](https://img.shields.io/badge/Deploy%20with-Portainer-blue?logo=docker)](https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/docker-stacks/telegram-bots-manager.yml)
[![Deploy with Docker Compose](https://img.shields.io/badge/Deploy%20with-Docker%20Compose-blue?logo=docker)](https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/docker-compose.yml)
[![One-Click Install](https://img.shields.io/badge/One--Click-Install-green?logo=github)](https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/install.sh)

## 📋 Visão Geral

Este projeto permite:
- ✅ Gerenciar múltiplos bots do Telegram simultaneamente
- ✅ Interface web moderna e responsiva (HTML/CSS/JavaScript puro)
- ✅ Monitoramento em tempo real via WebSocket
- ✅ Diferentes tipos de bots (Monitor, Deletador, Respondedor, etc.)
- ✅ Isolamento completo entre bots usando containers Docker
- ✅ Integração com Redis, PostgreSQL e MinIO existentes
- ✅ Acesso via `iabots.blackops7.cloud` (sem exposição de portas)

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │  Bot Manager    │    │  Bot Monitor    │
│   Web (HTML)    │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │     Redis       │    │   PostgreSQL    │
         │              │   (Cache/WS)    │    │   (Dados)       │
         │              └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Traefik     │
│  (Roteamento)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Bot Containers │
│  (Isolados)     │
└─────────────────┘
```

## 🚀 Instalação Rápida

### 🎯 Instalação em 1 Comando

```bash
curl -fsSL https://raw.githubusercontent.com/SKageyoshi/telegram-bots-manager/main/install.sh | bash
```

### 📦 Outras Formas de Instalação

<details>
<summary><strong>🐳 Docker Compose</strong></summary>

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/telegram-bots-manager.git
cd telegram-bots-manager

# Configurar variáveis
cp env.example .env
nano .env

# Iniciar serviços
docker-compose up -d
```

</details>

<details>
<summary><strong>📦 Portainer Stack</strong></summary>

1. Acesse seu Portainer
2. Vá em **Stacks** > **Add stack**
3. Cole o conteúdo do arquivo: [docker-stacks/telegram-bots-manager.yml](docker-stacks/telegram-bots-manager.yml)
4. Configure as variáveis de ambiente
5. Deploy da stack

</details>

<details>
<summary><strong>🐋 Docker Swarm</strong></summary>

```bash
# Baixar stack
curl -o telegram-bots-stack.yml https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/docker-stacks/telegram-bots-manager.yml

# Deploy
docker stack deploy -c telegram-bots-stack.yml telegram-bots
```

</details>

### ⚙️ Configuração

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `DOMAIN` | Domínio para acesso | Sim |
| `TELEGRAM_API_ID` | API ID do Telegram | Sim |
| `TELEGRAM_API_HASH` | API Hash do Telegram | Sim |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | Sim |

**Obter credenciais do Telegram:**
1. Acesse [my.telegram.org](https://my.telegram.org)
2. Crie uma nova aplicação
3. Copie o **API ID** e **API Hash**

## 📱 Interface Web

### Características:
- **100% HTML/CSS/JavaScript** - Sem frameworks complexos
- **Responsiva** - Funciona em desktop e mobile
- **Tempo Real** - Atualizações via WebSocket
- **Moderna** - Design glassmorphism com gradientes

### Funcionalidades:
- 📊 Dashboard com estatísticas em tempo real
- ➕ Criação de novos bots
- ▶️⏹️ Controle de start/stop dos bots
- 📋 Visualização de logs
- 🔄 Atualizações automáticas

## 🤖 Tipos de Bots

### 1. 📊 Monitor Bot
- Monitora grupos e canais
- Detecta palavras-chave específicas
- Envia alertas quando necessário
- Configuração via arquivo JSON

### 2. 🗑️ Deletador Bot
- Remove mensagens com termos específicos
- Suporte a regex patterns
- Lista de usuários protegidos
- Limpeza automática de mensagens antigas

### 3. 💬 Respondedor Bot
- Respostas automáticas baseadas em palavras-chave
- Respostas específicas por chat
- Delay configurável entre respostas
- Múltiplas respostas aleatórias

### 4. 💭 Comentador Bot
- Comenta automaticamente em posts
- Templates de comentários personalizáveis
- Filtros por tipo de conteúdo
- Agendamento de comentários

### 5. ⏰ Agendador Bot
- Envia mensagens programadas
- Suporte a horários fixos e intervalos
- Múltiplos chats simultâneos
- Controle de frequência

## ⚙️ Configuração de Bots

### Arquivo de Configuração
Cada bot possui um arquivo JSON em `bot-configs/`:

```json
{
  "monitor_groups": [-1001234567890],
  "monitor_keywords": ["palavra1", "palavra2"],
  "delete_keywords": ["spam", "promoção"],
  "response_messages": {
    "-1001234567890": ["Obrigado!", "Entendi!"]
  },
  "schedule_messages": [
    {
      "chat_id": -1001234567890,
      "text": "Mensagem programada",
      "time": "09:00",
      "active": true
    }
  ],
  "filters": {
    "min_message_length": 1,
    "max_message_length": 4096
  }
}
```

## 🔧 Comandos Úteis

### Gerenciamento da Stack
```bash
# Deploy
docker stack deploy -c docker-compose.yml telegram-bots

# Remover
docker stack rm telegram-bots

# Atualizar
docker service update --force telegram-bots_bot-manager
```

### Logs e Debug
```bash
# Logs do manager
docker service logs -f telegram-bots_bot-manager

# Logs do monitor
docker service logs -f telegram-bots_bot-monitor

# Logs de um bot específico
docker logs bot-nome_do_bot
```

### Containers de Bots
```bash
# Listar containers de bots
docker ps --filter "name=bot-"

# Parar um bot específico
docker stop bot-nome_do_bot

# Remover container de bot
docker rm bot-nome_do_bot
```

## 📊 Monitoramento

### Métricas Disponíveis:
- Total de bots
- Bots ativos/pausados/com erro
- Última atividade de cada bot
- Logs em tempo real
- Status de conexão WebSocket

### Logs:
- Logs de cada bot em `bot-logs/`
- Logs do sistema no banco PostgreSQL
- Logs de atividade no Redis

## 🛠️ Desenvolvimento

### Estrutura do Projeto:
```
├── docker-compose.yml          # Stack principal
├── env.example                 # Configurações de exemplo
├── bot-manager/               # Interface web e API
│   ├── main.py                # API FastAPI
│   ├── static/index.html      # Interface HTML
│   ├── requirements.txt       # Dependências Python
│   └── Dockerfile            # Container do manager
├── bot-monitor/               # Sistema de monitoramento
│   └── monitor.py            # Monitor de containers
├── bot-templates/             # Templates de bots
│   ├── base_bot.py           # Classe base
│   ├── monitor_bot.py        # Bot monitor
│   ├── deleter_bot.py        # Bot deletador
│   ├── responder_bot.py      # Bot respondedor
│   └── scheduler_bot.py      # Bot agendador
├── bot-sessions/             # Sessões do Telegram
├── bot-logs/                 # Logs dos bots
├── bot-scripts/              # Scripts gerados
└── bot-configs/              # Configurações dos bots
```

### Adicionando Novo Tipo de Bot:

1. Criar template em `bot-templates/novo_bot.py`
2. Herdar de `BaseTelegramBot`
3. Implementar lógica específica
4. Adicionar opção na interface web
5. Atualizar `main.py` para suportar o novo tipo

## 🔒 Segurança

- ✅ Nenhuma porta exposta (apenas Traefik)
- ✅ Containers isolados
- ✅ Sessões do Telegram criptografadas
- ✅ Logs seguros
- ✅ Acesso apenas via HTTPS

## 🐛 Troubleshooting

### Problemas Comuns:

1. **Bot não inicia:**
   - Verificar credenciais do Telegram
   - Verificar logs: `docker logs bot-nome_do_bot`
   - Verificar configuração JSON

2. **Interface não carrega:**
   - Verificar Traefik: `docker service logs telegram-bots_traefik`
   - Verificar DNS do domínio
   - Verificar certificado SSL

3. **WebSocket desconecta:**
   - Verificar Redis: `docker service logs telegram-bots_redis`
   - Verificar conectividade de rede
   - Reiniciar bot-manager

4. **Bot não responde:**
   - Verificar se está rodando: `docker ps | grep bot-`
   - Verificar logs do bot
   - Verificar configuração de palavras-chave

### Logs Importantes:
```bash
# Logs do sistema
docker service logs telegram-bots_bot-manager

# Logs de um bot específico
docker logs bot-nome_do_bot

# Logs do monitor
docker service logs telegram-bots_bot-monitor
```

## 📈 Performance

### Recursos Recomendados:
- **CPU**: 2+ cores
- **RAM**: 4GB+ (1GB por bot ativo)
- **Disco**: 20GB+ (para logs e sessões)
- **Rede**: Conexão estável

### Otimizações:
- Limpeza automática de logs antigos
- Compressão de sessões
- Cache Redis para dados frequentes
- Containers otimizados

## 🔄 Atualizações

### Atualizar Sistema:
```bash
# Parar stack
docker stack rm telegram-bots

# Atualizar código
git pull

# Deploy novamente
docker stack deploy -c docker-compose.yml telegram-bots
```

### Backup:
- Sessões: `bot-sessions/`
- Configurações: `bot-configs/`
- Logs: `bot-logs/`
- Banco: PostgreSQL dump

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs
2. Consultar esta documentação
3. Verificar configurações
4. Testar em ambiente isolado

## 🎯 Próximos Passos

- [ ] Interface de configuração visual
- [ ] Métricas avançadas
- [ ] Backup automático
- [ ] Notificações por email
- [ ] API REST completa
- [ ] Integração com webhooks

---

**Desenvolvido para máxima praticidade e eficiência!** 🚀
