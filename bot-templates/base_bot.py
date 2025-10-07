#!/usr/bin/env python3
"""
Template Base para Bots do Telegram
Classe base com funcionalidades comuns para todos os tipos de bots
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import redis
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User, Chat, Channel

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/app/logs/{os.getenv("BOT_NAME", "bot")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaseTelegramBot:
    """Classe base para todos os bots do Telegram"""
    
    def __init__(self, bot_name: str, phone_number: str, bot_type: str):
        self.bot_name = bot_name
        self.phone_number = phone_number
        self.bot_type = bot_type
        self.client = None
        self.session_string = None
        self.running = False
        
        # Configurações do Telegram
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        
        # Redis para comunicação
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
        
        # Configurações específicas do bot
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Carrega configurações específicas do bot"""
        config_file = f"/app/configs/{self.bot_name}.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar configurações: {e}")
        
        return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Retorna configurações padrão"""
        return {
            "monitor_groups": [],
            "monitor_keywords": [],
            "delete_keywords": [],
            "response_messages": {},
            "schedule_messages": [],
            "comment_templates": [],
            "filters": {
                "min_message_length": 1,
                "max_message_length": 4096,
                "allowed_languages": ["pt", "en"]
            }
        }
    
    async def start(self):
        """Inicia o bot"""
        try:
            logger.info(f"Iniciando bot {self.bot_name} do tipo {self.bot_type}")
            
            # Inicializar cliente Telegram
            await self.initialize_telegram_client()
            
            # Configurar handlers de eventos
            self.setup_event_handlers()
            
            # Executar lógica específica do bot
            await self.run_bot_logic()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar bot {self.bot_name}: {e}")
            raise
    
    async def initialize_telegram_client(self):
        """Inicializa o cliente do Telegram"""
        try:
            # Carregar sessão existente ou criar nova
            session_file = f"/app/sessions/{self.bot_name}.session"
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    self.session_string = f.read().strip()
            else:
                self.session_string = ""
            
            # Criar cliente
            self.client = TelegramClient(
                StringSession(self.session_string),
                self.api_id,
                self.api_hash
            )
            
            # Conectar e autenticar
            await self.client.start(phone=self.phone_number)
            
            # Salvar sessão
            session_string = self.client.session.save()
            with open(session_file, 'w') as f:
                f.write(session_string)
            
            logger.info(f"Cliente Telegram inicializado para {self.phone_number}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Telegram: {e}")
            raise
    
    def setup_event_handlers(self):
        """Configura handlers de eventos do Telegram"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handler para novas mensagens"""
            try:
                await self.process_new_message(event)
            except Exception as e:
                logger.error(f"Erro ao processar nova mensagem: {e}")
        
        @self.client.on(events.MessageEdited)
        async def handle_edited_message(event):
            """Handler para mensagens editadas"""
            try:
                await self.process_edited_message(event)
            except Exception as e:
                logger.error(f"Erro ao processar mensagem editada: {e}")
        
        @self.client.on(events.MessageDeleted)
        async def handle_deleted_message(event):
            """Handler para mensagens deletadas"""
            try:
                await self.process_deleted_message(event)
            except Exception as e:
                logger.error(f"Erro ao processar mensagem deletada: {e}")
    
    async def process_new_message(self, event):
        """Processa nova mensagem (implementar em subclasses)"""
        pass
    
    async def process_edited_message(self, event):
        """Processa mensagem editada (implementar em subclasses)"""
        pass
    
    async def process_deleted_message(self, event):
        """Processa mensagem deletada (implementar em subclasses)"""
        pass
    
    async def run_bot_logic(self):
        """Executa lógica específica do bot (implementar em subclasses)"""
        self.running = True
        logger.info(f"Bot {self.bot_name} executando...")
        
        # Loop principal
        while self.running:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Bot interrompido pelo usuário")
                self.running = False
    
    async def stop(self):
        """Para o bot"""
        logger.info(f"Parando bot {self.bot_name}")
        self.running = False
        if self.client:
            await self.client.disconnect()
    
    def log_activity(self, level: str, message: str):
        """Registra atividade do bot"""
        log_data = {
            "bot_name": self.bot_name,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            self.redis_client.publish("bot_activity", json.dumps(log_data))
        except Exception as e:
            logger.error(f"Erro ao publicar atividade no Redis: {e}")
    
    def is_message_relevant(self, message_text: str) -> bool:
        """Verifica se mensagem é relevante baseado nos filtros"""
        if not message_text:
            return False
        
        # Verificar comprimento
        min_length = self.config["filters"]["min_message_length"]
        max_length = self.config["filters"]["max_message_length"]
        
        if len(message_text) < min_length or len(message_text) > max_length:
            return False
        
        return True
    
    def contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Verifica se texto contém alguma das palavras-chave"""
        if not text or not keywords:
            return False
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    async def send_message(self, chat_id: int, message: str, reply_to: int = None):
        """Envia mensagem para um chat"""
        try:
            await self.client.send_message(chat_id, message, reply_to=reply_to)
            self.log_activity("info", f"Mensagem enviada para {chat_id}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            self.log_activity("error", f"Erro ao enviar mensagem: {e}")
    
    async def delete_message(self, chat_id: int, message_id: int):
        """Deleta uma mensagem"""
        try:
            await self.client.delete_messages(chat_id, message_id)
            self.log_activity("info", f"Mensagem {message_id} deletada de {chat_id}")
        except Exception as e:
            logger.error(f"Erro ao deletar mensagem: {e}")
            self.log_activity("error", f"Erro ao deletar mensagem: {e}")
    
    async def get_chat_info(self, chat_id: int) -> Optional[Dict]:
        """Obtém informações de um chat"""
        try:
            entity = await self.client.get_entity(chat_id)
            return {
                "id": entity.id,
                "title": getattr(entity, 'title', None),
                "username": getattr(entity, 'username', None),
                "type": type(entity).__name__
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do chat: {e}")
            return None
