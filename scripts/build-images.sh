#!/bin/bash

# 🤖 Script para build das imagens Docker
# Usado para criar as imagens oficiais do Telegram Bots Manager

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Building Telegram Bots Manager Images${NC}"

# Versão
VERSION=${1:-latest}
REGISTRY=${2:-telegrambots}

echo -e "${YELLOW}Version: $VERSION${NC}"
echo -e "${YELLOW}Registry: $REGISTRY${NC}"

# Build Manager Image
echo -e "${BLUE}Building Manager Image...${NC}"
docker build -t $REGISTRY/manager:$VERSION ./bot-manager
docker tag $REGISTRY/manager:$VERSION $REGISTRY/manager:latest

# Build Monitor Image
echo -e "${BLUE}Building Monitor Image...${NC}"
docker build -t $REGISTRY/monitor:$VERSION ./bot-monitor
docker tag $REGISTRY/monitor:$VERSION $REGISTRY/monitor:latest

# Build Base Bot Image
echo -e "${BLUE}Building Base Bot Image...${NC}"
docker build -t $REGISTRY/base-bot:$VERSION ./bot-templates
docker tag $REGISTRY/base-bot:$VERSION $REGISTRY/base-bot:latest

echo -e "${GREEN}✅ All images built successfully!${NC}"

# Push images (se especificado)
if [[ "$3" == "push" ]]; then
    echo -e "${BLUE}Pushing images to registry...${NC}"
    
    docker push $REGISTRY/manager:$VERSION
    docker push $REGISTRY/manager:latest
    docker push $REGISTRY/monitor:$VERSION
    docker push $REGISTRY/monitor:latest
    docker push $REGISTRY/base-bot:$VERSION
    docker push $REGISTRY/base-bot:latest
    
    echo -e "${GREEN}✅ All images pushed successfully!${NC}"
fi

echo -e "${GREEN}🎉 Build completed!${NC}"
