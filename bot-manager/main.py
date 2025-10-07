#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Bots do Telegram
Interface web para monitorar e controlar múltiplos bots
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

import redis
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://botuser:senha@postgres:5432/telegram_bots")

# Redis
redis_client = redis.from_url(REDIS_URL)

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True)
    status = Column(String, default="stopped")  # stopped, running, error
    bot_type = Column(String)  # monitor, deleter, responder, etc.
    last_activity = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, index=True)
    level = Column(String)  # info, warning, error
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class BotCreate(BaseModel):
    name: str
    phone_number: str
    bot_type: str

class BotUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None

class BotLogCreate(BaseModel):
    bot_id: int
    level: str
    message: str

# FastAPI app
app = FastAPI(title="Telegram Bots Manager", version="1.0.0")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# WebSocket connections
active_connections: List[WebSocket] = []

# Funções auxiliares
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

async def broadcast_status():
    """Envia status atual para todos os clientes conectados"""
    if not active_connections:
        return
    
    db = SessionLocal()
    try:
        bots = db.query(Bot).all()
        status_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "bots": [
                {
                    "id": bot.id,
                    "name": bot.name,
                    "status": bot.status,
                    "bot_type": bot.bot_type,
                    "last_activity": bot.last_activity.isoformat() if bot.last_activity else None,
                    "is_active": bot.is_active
                }
                for bot in bots
            ]
        }
        
        # Enviar para todas as conexões ativas
        for connection in active_connections:
            try:
                await connection.send_text(json.dumps(status_data))
            except:
                active_connections.remove(connection)
    finally:
        db.close()

def start_bot_container(bot_name: str, phone_number: str, bot_type: str):
    """Inicia um container para o bot"""
    try:
        # Criar script específico para o bot
        script_content = f"""
import asyncio
import logging
import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# Configuração
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = '{phone_number}'
BOT_NAME = '{bot_name}'
BOT_TYPE = '{bot_type}'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/app/logs/{{BOT_NAME}}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(BOT_NAME)

class TelegramBot:
    def __init__(self):
        self.client = None
        self.session_string = None
        
    async def start(self):
        try:
            # Inicializar cliente
            self.client = TelegramClient(
                StringSession(self.session_string),
                API_ID,
                API_HASH
            )
            
            await self.client.start(phone=PHONE_NUMBER)
            logger.info(f"Bot {{BOT_NAME}} iniciado com sucesso")
            
            # Executar lógica específica do tipo de bot
            if BOT_TYPE == 'monitor':
                await self.monitor_groups()
            elif BOT_TYPE == 'deleter':
                await self.delete_messages()
            elif BOT_TYPE == 'responder':
                await self.respond_messages()
            elif BOT_TYPE == 'commenter':
                await self.comment_posts()
            elif BOT_TYPE == 'scheduler':
                await self.send_scheduled_messages()
            else:
                logger.warning(f"Tipo de bot desconhecido: {{BOT_TYPE}}")
                
        except Exception as e:
            logger.error(f"Erro ao iniciar bot {{BOT_NAME}}: {{e}}")
            raise
    
    async def monitor_groups(self):
        '''Monitora grupos e canais'''
        logger.info("Iniciando monitoramento de grupos...")
        # Implementar lógica de monitoramento
        while True:
            await asyncio.sleep(60)
            logger.info("Monitorando grupos...")
    
    async def delete_messages(self):
        '''Deleta mensagens com termos específicos'''
        logger.info("Iniciando deleção de mensagens...")
        # Implementar lógica de deleção
        while True:
            await asyncio.sleep(30)
            logger.info("Verificando mensagens para deletar...")
    
    async def respond_messages(self):
        '''Responde mensagens automaticamente'''
        logger.info("Iniciando resposta automática...")
        # Implementar lógica de resposta
        while True:
            await asyncio.sleep(10)
            logger.info("Verificando mensagens para responder...")
    
    async def comment_posts(self):
        '''Comenta em posts automaticamente'''
        logger.info("Iniciando comentários automáticos...")
        # Implementar lógica de comentários
        while True:
            await asyncio.sleep(300)
            logger.info("Verificando posts para comentar...")
    
    async def send_scheduled_messages(self):
        '''Envia mensagens programadas'''
        logger.info("Iniciando envio de mensagens programadas...")
        # Implementar lógica de agendamento
        while True:
            await asyncio.sleep(3600)
            logger.info("Verificando mensagens agendadas...")

if __name__ == "__main__":
    bot = TelegramBot()
    asyncio.run(bot.start())
"""
        
        # Salvar script
        script_path = f"/app/bot-scripts/{bot_name}.py"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Criar comando docker run
        cmd = [
            "docker", "run", "-d",
            "--name", f"bot-{bot_name}",
            "--network", "minha_rede",
            "-e", f"TELEGRAM_API_ID={os.getenv('TELEGRAM_API_ID')}",
            "-e", f"TELEGRAM_API_HASH={os.getenv('TELEGRAM_API_HASH')}",
            "-v", f"/app/bot-sessions:/app/sessions",
            "-v", f"/app/bot-logs:/app/logs",
            "-v", f"/app/bot-scripts:/app/scripts",
            "python:3.11-slim",
            "python", f"/app/scripts/{bot_name}.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Container do bot {bot_name} iniciado com sucesso")
            return True
        else:
            logger.error(f"Erro ao iniciar container: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao criar bot {bot_name}: {e}")
        return False

def stop_bot_container(bot_name: str):
    """Para um container de bot"""
    try:
        cmd = ["docker", "stop", f"bot-{bot_name}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Remover container
            subprocess.run(["docker", "rm", f"bot-{bot_name}"], capture_output=True)
            logger.info(f"Container do bot {bot_name} parado com sucesso")
            return True
        else:
            logger.error(f"Erro ao parar container: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Erro ao parar bot {bot_name}: {e}")
        return False

# Rotas da API
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard principal - Interface HTML pura"""
    return FileResponse("static/index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_old(request: Request):
    """Dashboard antigo (Jinja2) - mantido para compatibilidade"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/bots")
async def get_bots():
    """Lista todos os bots"""
    db = SessionLocal()
    try:
        bots = db.query(Bot).all()
        return [
            {
                "id": bot.id,
                "name": bot.name,
                "phone_number": bot.phone_number,
                "status": bot.status,
                "bot_type": bot.bot_type,
                "last_activity": bot.last_activity.isoformat() if bot.last_activity else None,
                "is_active": bot.is_active,
                "created_at": bot.created_at.isoformat()
            }
            for bot in bots
        ]
    finally:
        db.close()

@app.post("/api/bots")
async def create_bot(bot_data: BotCreate):
    """Cria um novo bot"""
    db = SessionLocal()
    try:
        # Verificar se já existe
        existing_bot = db.query(Bot).filter(Bot.name == bot_data.name).first()
        if existing_bot:
            raise HTTPException(status_code=400, detail="Bot com este nome já existe")
        
        # Criar bot no banco
        bot = Bot(
            name=bot_data.name,
            phone_number=bot_data.phone_number,
            bot_type=bot_data.bot_type,
            status="stopped"
        )
        db.add(bot)
        db.commit()
        db.refresh(bot)
        
        # Iniciar container
        if start_bot_container(bot_data.name, bot_data.phone_number, bot_data.bot_type):
            bot.status = "running"
            db.commit()
        
        return {"message": "Bot criado com sucesso", "bot_id": bot.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: int):
    """Inicia um bot"""
    db = SessionLocal()
    try:
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        if start_bot_container(bot.name, bot.phone_number, bot.bot_type):
            bot.status = "running"
            bot.last_activity = datetime.utcnow()
            db.commit()
            return {"message": "Bot iniciado com sucesso"}
        else:
            bot.status = "error"
            db.commit()
            raise HTTPException(status_code=500, detail="Erro ao iniciar bot")
    finally:
        db.close()

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: int):
    """Para um bot"""
    db = SessionLocal()
    try:
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        if stop_bot_container(bot.name):
            bot.status = "stopped"
            db.commit()
            return {"message": "Bot parado com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao parar bot")
    finally:
        db.close()

@app.get("/api/bots/{bot_id}/logs")
async def get_bot_logs(bot_id: int, limit: int = 100):
    """Obtém logs de um bot"""
    db = SessionLocal()
    try:
        logs = db.query(BotLog).filter(BotLog.bot_id == bot_id).order_by(BotLog.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    finally:
        db.close()

# ===== ROTAS DE LISTAGEM DE CHATS =====

@app.get("/api/bots/{bot_id}/chats")
async def get_bot_chats(bot_id: int, chat_type: str = "all"):
    """Obtém lista de chats de um bot"""
    try:
        # Verificar se bot existe
        db = SessionLocal()
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        # Executar comando para obter chats
        container_name = f"bot-{bot.name}"
        
        # Comando para obter chats baseado no tipo
        if chat_type == "groups":
            cmd = ["docker", "exec", container_name, "python", "-c", 
                   "import asyncio; from advanced_bot import AdvancedBot; import os; "
                   "bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
                   "print(asyncio.run(bot.get_groups()))"]
        elif chat_type == "channels":
            cmd = ["docker", "exec", container_name, "python", "-c", 
                   "import asyncio; from advanced_bot import AdvancedBot; import os; "
                   "bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
                   "print(asyncio.run(bot.get_channels()))"]
        elif chat_type == "private":
            cmd = ["docker", "exec", container_name, "python", "-c", 
                   "import asyncio; from advanced_bot import AdvancedBot; import os; "
                   "bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
                   "print(asyncio.run(bot.get_private_chats()))"]
        else:  # all
            cmd = ["docker", "exec", container_name, "python", "-c", 
                   "import asyncio; from advanced_bot import AdvancedBot; import os; "
                   "bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
                   "print(asyncio.run(bot.get_all_chats()))"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            chats = json.loads(result.stdout)
            return chats
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao obter chats: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Erro ao obter chats do bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

@app.get("/api/bots/{bot_id}/chats/search")
async def search_bot_chats(bot_id: int, query: str):
    """Busca chats de um bot"""
    try:
        db = SessionLocal()
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        container_name = f"bot-{bot.name}"
        cmd = ["docker", "exec", container_name, "python", "-c", 
               f"import asyncio; from advanced_bot import AdvancedBot; import os; "
               f"bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
               f"print(asyncio.run(bot.search_chats('{query}')))"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            chats = json.loads(result.stdout)
            return chats
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar chats: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Erro ao buscar chats do bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

@app.get("/api/bots/{bot_id}/chats/{chat_id}/info")
async def get_chat_info(bot_id: int, chat_id: int):
    """Obtém informações detalhadas de um chat"""
    try:
        db = SessionLocal()
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        container_name = f"bot-{bot.name}"
        cmd = ["docker", "exec", container_name, "python", "-c", 
               f"import asyncio; from advanced_bot import AdvancedBot; import os; "
               f"bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
               f"print(asyncio.run(bot.get_chat_statistics({chat_id})))"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            chat_info = json.loads(result.stdout)
            return chat_info
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao obter informações do chat: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Erro ao obter informações do chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

@app.post("/api/bots/{bot_id}/chats/export")
async def export_chat_list(bot_id: int):
    """Exporta lista de chats de um bot"""
    try:
        db = SessionLocal()
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot não encontrado")
        
        container_name = f"bot-{bot.name}"
        cmd = ["docker", "exec", container_name, "python", "-c", 
               "import asyncio; from advanced_bot import AdvancedBot; import os; "
               "bot = AdvancedBot(os.getenv('BOT_NAME'), os.getenv('PHONE_NUMBER')); "
               "print(asyncio.run(bot.export_chat_list()))"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_path = result.stdout.strip()
            return {"message": "Lista de chats exportada com sucesso", "file_path": file_path}
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao exportar chats: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Erro ao exportar chats do bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para atualizações em tempo real"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Enviar status atual
            await broadcast_status()
            await asyncio.sleep(5)  # Atualizar a cada 5 segundos
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Inicialização
@app.on_event("startup")
async def startup_event():
    """Inicializa o sistema"""
    create_tables()
    logger.info("Sistema de gerenciamento de bots iniciado")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
