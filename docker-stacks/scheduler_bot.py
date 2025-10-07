#!/usr/bin/env python3
"""
Bot Agendador - Envia mensagens programadas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from base_bot import BaseTelegramBot

logger = logging.getLogger(__name__)

class SchedulerBot(BaseTelegramBot):
    """Bot para enviar mensagens programadas"""
    
    def __init__(self, bot_name: str, phone_number: str):
        super().__init__(bot_name, phone_number, "scheduler")
        self.scheduled_messages = self.config.get("schedule_messages", [])
        self.sent_count = 0
        
    async def run_bot_logic(self):
        """Lógica específica do bot agendador"""
        await super().run_bot_logic()
        
        # Lógica de agendamento
        while self.running:
            try:
                # Verificar mensagens agendadas
                await self.check_scheduled_messages()
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na lógica do agendador: {e}")
                await asyncio.sleep(60)
    
    async def check_scheduled_messages(self):
        """Verifica mensagens agendadas para envio"""
        current_time = datetime.now()
        
        for message in self.scheduled_messages:
            try:
                # Verificar se é hora de enviar
                if self.should_send_message(message, current_time):
                    await self.send_scheduled_message(message)
                    
            except Exception as e:
                logger.error(f"Erro ao verificar mensagem agendada: {e}")
    
    def should_send_message(self, message: Dict, current_time: datetime) -> bool:
        """Verifica se deve enviar a mensagem"""
        # Verificar se mensagem está ativa
        if not message.get("active", True):
            return False
        
        # Verificar se já foi enviada hoje
        last_sent = message.get("last_sent")
        if last_sent:
            last_sent_date = datetime.fromisoformat(last_sent)
            if last_sent_date.date() == current_time.date():
                return False
        
        # Verificar horário
        schedule_time = message.get("time")
        if schedule_time:
            try:
                hour, minute = map(int, schedule_time.split(":"))
                if current_time.hour == hour and current_time.minute == minute:
                    return True
            except:
                pass
        
        # Verificar intervalo
        interval_minutes = message.get("interval_minutes")
        if interval_minutes:
            last_sent = message.get("last_sent")
            if last_sent:
                last_sent_time = datetime.fromisoformat(last_sent)
                if current_time - last_sent_time >= timedelta(minutes=interval_minutes):
                    return True
            else:
                # Primeira execução
                return True
        
        return False
    
    async def send_scheduled_message(self, message: Dict):
        """Envia mensagem agendada"""
        try:
            chat_id = message.get("chat_id")
            text = message.get("text")
            
            if not chat_id or not text:
                logger.warning("Mensagem agendada inválida: chat_id ou text ausente")
                return
            
            # Enviar mensagem
            await self.send_message(chat_id, text)
            
            # Atualizar timestamp
            message["last_sent"] = datetime.now().isoformat()
            
            # Salvar configuração atualizada
            self.save_config()
            
            self.sent_count += 1
            self.log_activity("info", f"Mensagem agendada enviada para {chat_id}: {text[:100]}...")
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem agendada: {e}")
    
    def save_config(self):
        """Salva configuração atualizada"""
        try:
            config_file = f"/app/configs/{self.bot_name}.json"
            import json
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")

if __name__ == "__main__":
    import os
    
    bot_name = os.getenv("BOT_NAME", "scheduler_bot")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not phone_number:
        logger.error("PHONE_NUMBER não definido")
        exit(1)
    
    bot = SchedulerBot(bot_name, phone_number)
    asyncio.run(bot.start())
