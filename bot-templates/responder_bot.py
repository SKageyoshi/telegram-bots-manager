#!/usr/bin/env python3
"""
Bot Respondedor - Responde mensagens automaticamente
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List

from base_bot import BaseTelegramBot

logger = logging.getLogger(__name__)

class ResponderBot(BaseTelegramBot):
    """Bot para responder mensagens automaticamente"""
    
    def __init__(self, bot_name: str, phone_number: str):
        super().__init__(bot_name, phone_number, "responder")
        self.response_messages = self.config.get("response_messages", {})
        self.auto_responses = self.config.get("auto_responses", [])
        self.response_delay = self.config.get("response_delay_seconds", 2)
        self.responded_count = 0
        
    async def process_new_message(self, event):
        """Processa novas mensagens para resposta automática"""
        try:
            # Verificar se deve responder
            if not self.should_respond(event):
                return
            
            # Aguardar delay configurado
            await asyncio.sleep(self.response_delay)
            
            # Gerar resposta
            response_text = self.generate_response(event)
            if response_text:
                await self.send_message(event.chat_id, response_text, reply_to=event.message.id)
                self.responded_count += 1
                
                self.log_activity("info", f"Resposta enviada para {event.chat_id}: {response_text[:100]}...")
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no respondedor: {e}")
    
    def should_respond(self, event) -> bool:
        """Verifica se deve responder à mensagem"""
        # Não responder a si mesmo
        if event.sender_id == event.client.me.id:
            return False
        
        # Verificar se mensagem é relevante
        message_text = event.message.text or ""
        if not self.is_message_relevant(message_text):
            return False
        
        # Verificar palavras-chave de resposta
        if self.auto_responses:
            for auto_response in self.auto_responses:
                keywords = auto_response.get("keywords", [])
                if keywords and self.contains_keywords(message_text, keywords):
                    return True
        
        # Verificar respostas específicas por chat
        chat_id = event.chat_id
        if str(chat_id) in self.response_messages:
            return True
        
        return False
    
    def generate_response(self, event) -> str:
        """Gera resposta baseada na mensagem"""
        message_text = event.message.text or ""
        chat_id = event.chat_id
        
        # Resposta específica por chat
        if str(chat_id) in self.response_messages:
            responses = self.response_messages[str(chat_id)]
            if isinstance(responses, list):
                return random.choice(responses)
            return responses
        
        # Resposta baseada em palavras-chave
        if self.auto_responses:
            for auto_response in self.auto_responses:
                keywords = auto_response.get("keywords", [])
                if keywords and self.contains_keywords(message_text, keywords):
                    responses = auto_response.get("responses", [])
                    if responses:
                        return random.choice(responses)
        
        # Resposta padrão
        default_responses = [
            "Obrigado pela mensagem!",
            "Entendi, obrigado!",
            "Vou verificar isso para você.",
            "Interessante, me conte mais!",
            "Perfeito, anotado!"
        ]
        
        return random.choice(default_responses)
    
    async def run_bot_logic(self):
        """Lógica específica do bot respondedor"""
        await super().run_bot_logic()
        
        # Lógica adicional de resposta
        while self.running:
            try:
                # Verificar mensagens não respondidas
                await self.check_unanswered_messages()
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro na lógica do respondedor: {e}")
                await asyncio.sleep(60)
    
    async def check_unanswered_messages(self):
        """Verifica mensagens não respondidas (implementação futura)"""
        # Esta função pode ser implementada para verificar mensagens antigas
        # que não foram respondidas e responder a elas
        pass

if __name__ == "__main__":
    import os
    
    bot_name = os.getenv("BOT_NAME", "responder_bot")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not phone_number:
        logger.error("PHONE_NUMBER não definido")
        exit(1)
    
    bot = ResponderBot(bot_name, phone_number)
    asyncio.run(bot.start())
