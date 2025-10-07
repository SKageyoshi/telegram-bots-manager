#!/usr/bin/env python3
"""
Bot Deletador - Deleta mensagens com termos específicos
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List

from base_bot import BaseTelegramBot

logger = logging.getLogger(__name__)

class DeleterBot(BaseTelegramBot):
    """Bot para deletar mensagens com termos específicos"""
    
    def __init__(self, bot_name: str, phone_number: str):
        super().__init__(bot_name, phone_number, "deleter")
        self.delete_keywords = self.config.get("delete_keywords", [])
        self.delete_patterns = self.config.get("delete_patterns", [])
        self.protected_users = self.config.get("protected_users", [])
        self.max_message_age = self.config.get("max_message_age_hours", 24)
        self.deleted_count = 0
        
    async def process_new_message(self, event):
        """Processa novas mensagens para deleção"""
        try:
            # Verificar se usuário está protegido
            user_id = event.sender_id
            if user_id in self.protected_users:
                return
            
            # Verificar idade da mensagem
            message_date = event.message.date
            if datetime.now() - message_date > timedelta(hours=self.max_message_age):
                return
            
            message_text = event.message.text or ""
            
            # Verificar se deve deletar
            if self.should_delete_message(message_text):
                await self.delete_message(event.chat_id, event.message.id)
                self.deleted_count += 1
                
                self.log_activity("info", f"Mensagem deletada de {event.chat_id}: {message_text[:100]}...")
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no deletador: {e}")
    
    def should_delete_message(self, message_text: str) -> bool:
        """Verifica se mensagem deve ser deletada"""
        if not message_text:
            return False
        
        # Verificar palavras-chave
        if self.delete_keywords:
            if self.contains_keywords(message_text, self.delete_keywords):
                return True
        
        # Verificar padrões regex
        if self.delete_patterns:
            for pattern in self.delete_patterns:
                try:
                    if re.search(pattern, message_text, re.IGNORECASE):
                        return True
                except re.error:
                    logger.warning(f"Padrão regex inválido: {pattern}")
        
        return False
    
    async def run_bot_logic(self):
        """Lógica específica do bot deletador"""
        await super().run_bot_logic()
        
        # Lógica adicional de limpeza
        while self.running:
            try:
                # Limpeza periódica de mensagens antigas
                await self.cleanup_old_messages()
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro na lógica do deletador: {e}")
                await asyncio.sleep(60)
    
    async def cleanup_old_messages(self):
        """Limpeza de mensagens antigas"""
        try:
            # Esta função pode ser implementada para limpar mensagens antigas
            # baseado em critérios específicos
            self.log_activity("info", f"Limpeza periódica executada. Total deletado: {self.deleted_count}")
            
        except Exception as e:
            logger.error(f"Erro na limpeza periódica: {e}")

if __name__ == "__main__":
    import os
    
    bot_name = os.getenv("BOT_NAME", "deleter_bot")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not phone_number:
        logger.error("PHONE_NUMBER não definido")
        exit(1)
    
    bot = DeleterBot(bot_name, phone_number)
    asyncio.run(bot.start())
