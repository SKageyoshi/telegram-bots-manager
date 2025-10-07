#!/bin/bash

# 🤖 Telegram Bots Manager - Instalador Oficial
# Instalação automática para diferentes ambientes

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🤖 TELEGRAM BOTS MANAGER - INSTALADOR             ║"
echo "║                                                              ║"
echo "║              Instalação Automática v1.0.0                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

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

# Verificar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Sistema operacional detectado: $OS"
}

# Verificar Docker
check_docker() {
    print_status "Verificando Docker..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado!"
        print_status "Instalando Docker..."
        install_docker
    else
        print_success "Docker está instalado"
    fi
}

# Instalar Docker
install_docker() {
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        print_success "Docker instalado com sucesso"
        print_warning "Reinicie o terminal e execute novamente o script"
        exit 0
    else
        print_error "Instale o Docker manualmente: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# Detectar ambiente
detect_environment() {
    print_status "Detectando ambiente..."
    
    # Verificar se está em Docker Swarm
    if docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null | grep -q "active"; then
        ENVIRONMENT="swarm"
        print_success "Docker Swarm detectado"
    # Verificar se Portainer está disponível
    elif docker ps --format "table {{.Names}}" | grep -q "portainer"; then
        ENVIRONMENT="portainer"
        print_success "Portainer detectado"
    # Verificar se Docker Compose está disponível
    elif command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        ENVIRONMENT="compose"
        print_success "Docker Compose detectado"
    else
        ENVIRONMENT="docker"
        print_success "Docker simples detectado"
    fi
}

# Configurar variáveis
configure_environment() {
    print_status "Configurando variáveis de ambiente..."
    
    # Solicitar informações do usuário
    echo -e "${YELLOW}Configuração do Telegram Bots Manager${NC}"
    echo ""
    
    read -p "🌐 Domínio para acesso (ex: bots.seudominio.com): " DOMAIN
    read -p "📱 API ID do Telegram: " TELEGRAM_API_ID
    read -p "🔑 API Hash do Telegram: " TELEGRAM_API_HASH
    read -p "🔐 Senha do PostgreSQL: " POSTGRES_PASSWORD
    read -p "🔐 Chave secreta (deixe vazio para gerar): " SECRET_KEY
    
    # Gerar chave secreta se não fornecida
    if [[ -z "$SECRET_KEY" ]]; then
        SECRET_KEY=$(openssl rand -base64 32)
        print_success "Chave secreta gerada automaticamente"
    fi
    
    # Configurações padrão
    MINIO_ACCESS_KEY="admin"
    MINIO_SECRET_KEY="$(openssl rand -base64 16)"
    
    # Criar arquivo .env
    cat > .env << EOF
# Telegram Bots Manager Configuration
DOMAIN=${DOMAIN}
TELEGRAM_API_ID=${TELEGRAM_API_ID}
TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
SECRET_KEY=${SECRET_KEY}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
EOF
    
    print_success "Arquivo .env criado"
}

# Instalar no Docker Swarm
install_swarm() {
    print_status "Instalando no Docker Swarm..."
    
    # Baixar stack
    curl -o telegram-bots-stack.yml https://raw.githubusercontent.com/SEU-USERNAME/telegram-bots-manager/main/docker-stacks/telegram-bots-manager.yml
    
    # Deploy da stack
    docker stack deploy -c telegram-bots-stack.yml telegram-bots
    
    print_success "Stack deployada com sucesso!"
    print_status "Acesse: https://${DOMAIN}"
}

# Instalar no Portainer
install_portainer() {
    print_status "Instalando no Portainer..."
    
    print_warning "Para instalar no Portainer:"
    echo "1. Acesse seu Portainer"
    echo "2. Vá em 'Stacks' > 'Add stack'"
    echo "3. Cole o conteúdo do arquivo: docker-stacks/telegram-bots-manager.yml"
    echo "4. Configure as variáveis de ambiente"
    echo "5. Deploy da stack"
    echo ""
    print_status "URL da stack: https://raw.githubusercontent.com/SEU-USERNAME/telegram-bots-manager/main/docker-stacks/telegram-bots-manager.yml"
}

# Instalar com Docker Compose
install_compose() {
    print_status "Instalando com Docker Compose..."
    
    # Baixar docker-compose.yml
    curl -o docker-compose.yml https://raw.githubusercontent.com/SEU-USERNAME/telegram-bots-manager/main/docker-compose.yml
    
    # Iniciar serviços
    docker-compose up -d
    
    print_success "Serviços iniciados com sucesso!"
    print_status "Acesse: https://${DOMAIN}"
}

# Instalar com Docker simples
install_docker_simple() {
    print_status "Instalando com Docker simples..."
    
    # Criar rede
    docker network create telegram_bots_network 2>/dev/null || true
    
    # Executar container
    docker run -d \
        --name telegram-bots-manager \
        --network telegram_bots_network \
        -p 8000:8000 \
        -e TELEGRAM_API_ID=${TELEGRAM_API_ID} \
        -e TELEGRAM_API_HASH=${TELEGRAM_API_HASH} \
        -e SECRET_KEY=${SECRET_KEY} \
        telegrambots/manager:latest
    
    print_success "Container iniciado com sucesso!"
    print_status "Acesse: http://localhost:8000"
}

# Verificar instalação
verify_installation() {
    print_status "Verificando instalação..."
    
    sleep 10
    
    if [[ "$ENVIRONMENT" == "swarm" ]]; then
        if docker service ls | grep -q "telegram-bots"; then
            print_success "Instalação verificada com sucesso!"
        else
            print_error "Falha na verificação da instalação"
        fi
    elif [[ "$ENVIRONMENT" == "compose" ]]; then
        if docker-compose ps | grep -q "Up"; then
            print_success "Instalação verificada com sucesso!"
        else
            print_error "Falha na verificação da instalação"
        fi
    else
        if docker ps | grep -q "telegram-bots-manager"; then
            print_success "Instalação verificada com sucesso!"
        else
            print_error "Falha na verificação da instalação"
        fi
    fi
}

# Mostrar informações pós-instalação
show_post_install_info() {
    echo ""
    echo -e "${GREEN}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉${NC}"
    echo ""
    echo -e "${BLUE}📋 Informações importantes:${NC}"
    echo "  • Interface web: https://${DOMAIN}"
    echo "  • Documentação: https://github.com/seu-usuario/telegram-bots-manager"
    echo "  • Suporte: https://github.com/seu-usuario/telegram-bots-manager/issues"
    echo ""
    echo -e "${BLUE}🔧 Comandos úteis:${NC}"
    if [[ "$ENVIRONMENT" == "swarm" ]]; then
        echo "  • Ver status: docker stack services telegram-bots"
        echo "  • Ver logs: docker service logs -f telegram-bots_telegram-bots-manager"
        echo "  • Parar: docker stack rm telegram-bots"
    elif [[ "$ENVIRONMENT" == "compose" ]]; then
        echo "  • Ver status: docker-compose ps"
        echo "  • Ver logs: docker-compose logs -f"
        echo "  • Parar: docker-compose down"
    else
        echo "  • Ver logs: docker logs -f telegram-bots-manager"
        echo "  • Parar: docker stop telegram-bots-manager"
    fi
    echo ""
    echo -e "${YELLOW}⚠️  Próximos passos:${NC}"
    echo "  1. Acesse a interface web"
    echo "  2. Configure seus bots do Telegram"
    echo "  3. Leia a documentação para funcionalidades avançadas"
    echo ""
    print_success "Bem-vindo ao Telegram Bots Manager! 🚀"
}

# Função principal
main() {
    detect_os
    check_docker
    detect_environment
    configure_environment
    
    case $ENVIRONMENT in
        "swarm")
            install_swarm
            ;;
        "portainer")
            install_portainer
            ;;
        "compose")
            install_compose
            ;;
        "docker")
            install_docker_simple
            ;;
    esac
    
    verify_installation
    show_post_install_info
}

# Executar instalação
main "$@"
