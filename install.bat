@echo off
echo 🤖 Instalando Telegram Bots Manager...

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não encontrado. Instale o Docker Desktop primeiro:
    echo    https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não encontrado. Instale o Docker Compose primeiro:
    echo    https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Clonar repositório se não existir
if not exist "telegram-bots-manager" (
    echo 📥 Clonando repositório...
    git clone https://github.com/SKageyoshi/telegram-bots-manager.git
)

cd telegram-bots-manager

REM Construir e executar
echo 🔨 Construindo imagem Docker...
docker-compose up -d --build

echo ✅ Instalação concluída!
echo 🌐 Acesse: http://localhost:8000
echo.
echo 📋 Comandos úteis:
echo    docker-compose logs -f    # Ver logs
echo    docker-compose down       # Parar
echo    docker-compose restart    # Reiniciar
pause
