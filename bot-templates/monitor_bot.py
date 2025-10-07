#!/usr/bin/env python3
"""
Bot Monitor - Monitora grupos e canais do Telegram
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

from base_bot import BaseTelegramBot

logger = logging.getLogger(__name__)

class MonitorBot(BaseTelegramBot):
    """Bot para monitorar grupos e canais"""
    
    def __init__(self, bot_name: str, phone_number: str):
        super().__init__(bot_name, phone_number, "monitor")
        self.monitored_chats = self.config.get("monitor_groups", [])
        self.keywords = self.config.get("monitor_keywords", [])
        self.alert_threshold = self.config.get("alert_threshold", 5)
        self.message_count = 0
        
    async def process_new_message(self, event):
        """Processa novas mensagens para monitoramento"""
        try:
            # Verificar se é de um chat monitorado
            chat_id = event.chat_id
            if chat_id not in self.monitored_chats:
                return
            
            # Verificar se mensagem é relevante
            message_text = event.message.text or ""
            if not self.is_message_relevant(message_text):
                return
            
            # Verificar palavras-chave
            if self.keywords and not self.contains_keywords(message_text, self.keywords):
                return
            
            # Incrementar contador
            self.message_count += 1
            
            # Log da atividade
            self.log_activity("info", f"Mensagem monitorada de {chat_id}: {message_text[:100]}...")
            
            # Verificar se atingiu threshold de alerta
            if self.message_count >= self.alert_threshold:
                await self.send_alert(chat_id, message_text)
                self.message_count = 0
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no monitor: {e}")
    
    async def send_alert(self, chat_id: int, message_text: str):
        """Envia alerta quando threshold é atingido"""
        try:
            alert_message = f"🚨 ALERTA DE MONITORAMENTO\n\n"
            alert_message += f"Chat: {chat_id}\n"
            alert_message += f"Mensagens monitoradas: {self.message_count}\n"
            alert_message += f"Última mensagem: {message_text[:200]}...\n"
            alert_message += f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            # Aqui você pode enviar para um chat específico de alertas
            # ou salvar no banco de dados
            self.log_activity("warning", f"Alerta enviado para chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")
    
    async def run_bot_logic(self):
        """Lógica específica do bot monitor"""
        await super().run_bot_logic()
        
        # Lógica adicional de monitoramento
        while self.running:
            try:
                # Verificar status dos chats monitorados
                await self.check_monitored_chats()
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na lógica do monitor: {e}")
                await asyncio.sleep(30)
    
    async def check_monitored_chats(self):
        """Verifica status dos chats monitorados"""
        for chat_id in self.monitored_chats:
            try:
                chat_info = await self.get_chat_info(chat_id)
                if chat_info:
                    self.log_activity("info", f"Chat {chat_id} está ativo: {chat_info.get('title', 'Sem título')}")
                else:
                    self.log_activity("warning", f"Não foi possível acessar chat {chat_id}")
                    
            except Exception as e:
                logger.error(f"Erro ao verificar chat {chat_id}: {e}")

if __name__ == "__main__":
    import os
    
    bot_name = os.getenv("BOT_NAME", "monitor_bot")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not phone_number:
        logger.error("PHONE_NUMBER não definido")
        exit(1)
    
    bot = MonitorBot(bot_name, phone_number)
    asyncio.run(bot.start())
