#!/bin/bash

# 🤖 Script de Setup - Sistema de Bots do Telegram
# Configuração automática do ambiente

set -e

echo "🚀 Iniciando setup do Sistema de Bots do Telegram..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Docker está rodando
print_status "Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando ou não está instalado!"
    exit 1
fi
print_success "Docker está rodando"

# Verificar se está em modo Swarm
print_status "Verificando Docker Swarm..."
if ! docker node ls > /dev/null 2>&1; then
    print_warning "Docker Swarm não está inicializado. Inicializando..."
    docker swarm init
fi
print_success "Docker Swarm está ativo"

# Verificar rede existente
print_status "Verificando rede 'minha_rede'..."
if ! docker network ls | grep -q "minha_rede"; then
    print_warning "Rede 'minha_rede' não encontrada. Criando..."
    docker network create --driver overlay minha_rede
fi
print_success "Rede 'minha_rede' está disponível"

# Criar diretórios necessários
print_status "Criando diretórios..."
mkdir -p bot-sessions bot-logs bot-scripts bot-configs
print_success "Diretórios criados"

# Verificar arquivo .env
print_status "Verificando configurações..."
if [ ! -f .env ]; then
    print_warning "Arquivo .env não encontrado. Copiando do exemplo..."
    cp env.example .env
    print_warning "IMPORTANTE: Edite o arquivo .env com suas credenciais do Telegram!"
    print_warning "Execute: nano .env"
    read -p "Pressione Enter após editar o .env..."
fi

# Verificar se .env tem as configurações necessárias
if ! grep -q "TELEGRAM_API_ID=" .env || ! grep -q "TELEGRAM_API_HASH=" .env; then
    print_error "Arquivo .env não está configurado corretamente!"
    print_error "Configure TELEGRAM_API_ID e TELEGRAM_API_HASH no arquivo .env"
    exit 1
fi
print_success "Configurações verificadas"

# Verificar se os serviços existentes estão rodando
print_status "Verificando serviços existentes..."

# Verificar Redis
if ! docker service ls | grep -q "redis"; then
    print_warning "Serviço Redis não encontrado. Certifique-se de que está rodando."
fi

# Verificar PostgreSQL
if ! docker service ls | grep -q "postgres"; then
    print_warning "Serviço PostgreSQL não encontrado. Certifique-se de que está rodando."
fi

# Verificar MinIO
if ! docker service ls | grep -q "minio"; then
    print_warning "Serviço MinIO não encontrado. Certifique-se de que está rodando."
fi

print_success "Verificação de serviços concluída"

# Build da imagem do bot-manager
print_status "Fazendo build da imagem do bot-manager..."
docker build -t telegram-bots-manager ./bot-manager
print_success "Build concluído"

# Deploy da stack
print_status "Fazendo deploy da stack..."
docker stack deploy -c docker-compose.yml telegram-bots
print_success "Stack deployada"

# Aguardar serviços iniciarem
print_status "Aguardando serviços iniciarem..."
sleep 10

# Verificar status dos serviços
print_status "Verificando status dos serviços..."
docker stack services telegram-bots

# Aguardar mais um pouco para garantir que tudo está rodando
print_status "Aguardando inicialização completa..."
sleep 30

# Verificar se a interface está acessível
print_status "Testando interface web..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200"; then
    print_success "Interface web está acessível"
else
    print_warning "Interface web pode não estar acessível ainda. Aguarde alguns minutos."
fi

# Mostrar informações finais
echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📋 Informações importantes:"
echo "  • Interface web: https://iabots.blackops7.cloud"
echo "  • Logs do manager: docker service logs -f telegram-bots_bot-manager"
echo "  • Logs do monitor: docker service logs -f telegram-bots_bot-monitor"
echo "  • Status da stack: docker stack services telegram-bots"
echo ""
echo "🔧 Comandos úteis:"
echo "  • Parar stack: docker stack rm telegram-bots"
echo "  • Atualizar: docker service update --force telegram-bots_bot-manager"
echo "  • Ver logs: docker service logs -f telegram-bots_bot-manager"
echo ""
echo "📚 Documentação completa: README.md"
echo ""
print_success "Sistema pronto para uso! 🚀"
