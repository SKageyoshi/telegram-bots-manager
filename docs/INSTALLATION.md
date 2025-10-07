# 🚀 Guia de Instalação - Telegram Bots Manager

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Domínio configurado (opcional, mas recomendado)
- Credenciais do Telegram (API ID e API Hash)

## 🎯 Métodos de Instalação

### 1. 🚀 Instalação Automática (Recomendado)

```bash
# Baixar e executar o instalador
curl -fsSL https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/install.sh | bash
```

### 2. 🐳 Docker Compose

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

### 3. 📦 Portainer Stack

1. Acesse seu Portainer
2. Vá em **Stacks** > **Add stack**
3. Cole o conteúdo do arquivo `docker-stacks/telegram-bots-manager.yml`
4. Configure as variáveis de ambiente
5. Clique em **Deploy the stack**

### 4. 🐋 Docker Swarm

```bash
# Baixar stack
curl -o telegram-bots-stack.yml https://raw.githubusercontent.com/seu-usuario/telegram-bots-manager/main/docker-stacks/telegram-bots-manager.yml

# Deploy
docker stack deploy -c telegram-bots-stack.yml telegram-bots
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `DOMAIN` | Domínio para acesso | Sim |
| `TELEGRAM_API_ID` | API ID do Telegram | Sim |
| `TELEGRAM_API_HASH` | API Hash do Telegram | Sim |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | Sim |
| `SECRET_KEY` | Chave secreta para JWT | Não (gerada automaticamente) |
| `MINIO_ACCESS_KEY` | Chave de acesso do MinIO | Não (padrão: admin) |
| `MINIO_SECRET_KEY` | Chave secreta do MinIO | Não (gerada automaticamente) |

### Obter Credenciais do Telegram

1. Acesse [my.telegram.org](https://my.telegram.org)
2. Faça login com seu número de telefone
3. Vá em **API development tools**
4. Crie uma nova aplicação
5. Copie o **API ID** e **API Hash**

## 🌐 Configuração de Domínio

### Com Traefik (Recomendado)

```yaml
# docker-compose.yml
labels:
  - traefik.enable=true
  - traefik.http.routers.telegram-bots.rule=Host(`bots.seudominio.com`)
  - traefik.http.routers.telegram-bots.tls=true
  - traefik.http.routers.telegram-bots.tls.certresolver=letsencrypt
```

### Sem Traefik

```yaml
# docker-compose.yml
ports:
  - "8000:8000"
```

Acesse: `http://localhost:8000`

## 🔧 Pós-Instalação

### 1. Acessar Interface

- **Com domínio**: `https://bots.seudominio.com`
- **Local**: `http://localhost:8000`

### 2. Criar Primeiro Bot

1. Clique em **"Novo Bot"**
2. Preencha:
   - Nome do bot
   - Número do telefone
   - Tipo do bot
3. Clique em **"Criar Bot"**

### 3. Configurar Bot

1. Acesse a lista de bots
2. Clique em **"Chats"** para ver chats disponíveis
3. Configure as regras de cada bot
4. Inicie o bot

## 🐛 Troubleshooting

### Problemas Comuns

#### Bot não inicia
```bash
# Verificar logs
docker logs bot-nome_do_bot

# Verificar configuração
docker exec bot-nome_do_bot cat /app/configs/nome_do_bot.json
```

#### Interface não carrega
```bash
# Verificar status dos serviços
docker-compose ps

# Verificar logs do manager
docker-compose logs telegram-bots-manager
```

#### Erro de permissões
```bash
# Verificar permissões do Docker
sudo usermod -aG docker $USER
# Reiniciar terminal
```

### Logs Importantes

```bash
# Logs do manager
docker-compose logs -f telegram-bots-manager

# Logs de um bot específico
docker logs -f bot-nome_do_bot

# Logs do monitor
docker-compose logs -f telegram-bots-monitor
```

## 📚 Próximos Passos

1. **Leia a documentação completa**: [README.md](../README.md)
2. **Configure seus bots**: [Guia de Configuração](CONFIGURATION.md)
3. **Explore funcionalidades**: [Guia de Uso](USAGE.md)
4. **Participe da comunidade**: [GitHub Discussions](https://github.com/seu-usuario/telegram-bots-manager/discussions)

## 🆘 Suporte

- **GitHub Issues**: [Reportar problemas](https://github.com/seu-usuario/telegram-bots-manager/issues)
- **Documentação**: [docs/](../docs/)
- **Discord**: [Servidor da comunidade](https://discord.gg/telegram-bots-manager)

---

**Desenvolvido com ❤️ para a comunidade Telegram**
