# 🔄 COMANDOS PARA ATUALIZAR NO VPS

## Execute estes comandos no VPS para atualizar:

```bash
# 1. Ir para o diretório do projeto
cd /opt/telegram-bots

# 2. Baixar mudanças do GitHub
git pull origin main

# 3. Rebuild da imagem Docker
docker build -t iabots-manager:latest .

# 4. Atualizar serviço no Docker Swarm
docker service update --force iabots-manager

# 5. Aguardar atualização (30 segundos)
sleep 30

# 6. Testar se está funcionando
curl -H "Host: iabots.blackops7.cloud" https://iabots.blackops7.cloud | head -10

# 7. Ver logs do serviço
docker service logs iabots-manager --tail 10
```

## ✅ RESULTADO ESPERADO:
- Interface atualizada com "Taila IaBots Manager - by Denver"
- Todas as funcionalidades funcionando
- Sem erros nos logs
