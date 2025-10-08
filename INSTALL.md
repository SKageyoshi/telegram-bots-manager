# 🤖 Telegram Bots Manager - Instalação

## 🚀 Instalação Rápida com Docker

### Pré-requisitos
- Docker instalado
- Docker Compose instalado
- Git instalado

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/SKageyoshi/telegram-bots-manager.git
cd telegram-bots-manager
```

2. **Execute com Docker Compose:**
```bash
docker-compose up -d
```

3. **Acesse a aplicação:**
- URL: http://localhost:8000
- Interface moderna com tema Telegram

### 🛠️ Comandos Úteis

```bash
# Parar a aplicação
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Atualizar
git pull origin main
docker-compose up -d --build
```

### 🌐 Para Produção (com domínio próprio)

1. **Configure seu domínio** no DNS apontando para o servidor
2. **Use Traefik** para SSL automático
3. **Configure variáveis de ambiente** se necessário

### 📱 Funcionalidades

- ✅ Interface web moderna
- ✅ Tema Telegram oficial
- ✅ Dashboard responsivo
- ✅ API REST
- ✅ Gerenciamento de bots
- ✅ Estatísticas em tempo real

### 🆘 Suporte

- GitHub: https://github.com/SKageyoshi/telegram-bots-manager
- Issues: Use a aba Issues do GitHub
