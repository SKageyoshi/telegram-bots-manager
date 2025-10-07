#!/usr/bin/env python3
"""
Bot Avançado - Funcionalidades completas do Telegram
Inclui todas as funcionalidades básicas e avançadas
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from telethon.tl.types import User, Chat, Channel, MessageMediaPhoto, MessageMediaDocument
from telethon.tl.functions.channels import CreateChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.types import ChatAdminRights

from base_bot import BaseTelegramBot

logger = logging.getLogger(__name__)

class AdvancedBot(BaseTelegramBot):
    """Bot avançado com todas as funcionalidades do Telegram"""
    
    def __init__(self, bot_name: str, phone_number: str):
        super().__init__(bot_name, phone_number, "advanced")
        
        # Funcionalidades básicas
        self.read_enabled = self.config.get("read_enabled", True)
        self.write_enabled = self.config.get("write_enabled", True)
        self.media_enabled = self.config.get("media_enabled", True)
        
        # Filtros e reconhecimento
        self.keywords = self.config.get("keywords", [])
        self.regex_patterns = self.config.get("regex_patterns", [])
        self.media_filters = self.config.get("media_filters", [])
        self.user_filters = self.config.get("user_filters", {})
        
        # Substituição de conteúdo
        self.replace_rules = self.config.get("replace_rules", [])
        self.link_replacements = self.config.get("link_replacements", {})
        
        # Funcionalidades sensíveis (com avisos)
        self.member_management = self.config.get("member_management", {})
        self.chat_management = self.config.get("chat_management", {})
        
        # Monitoramento e clonagem
        self.monitor_chats = self.config.get("monitor_chats", [])
        self.clone_rules = self.config.get("clone_rules", [])
        
        # Sistema de streaming
        self.streaming_config = self.config.get("streaming", {})
        
        # Mensagens periódicas
        self.scheduled_messages = self.config.get("scheduled_messages", [])
        
        # Contadores
        self.messages_processed = 0
        self.messages_sent = 0
        self.messages_deleted = 0
        self.members_managed = 0
        
    async def process_new_message(self, event):
        """Processa novas mensagens com todas as funcionalidades"""
        try:
            self.messages_processed += 1
            
            # Verificar se deve processar
            if not self.should_process_message(event):
                return
            
            # Aplicar filtros
            if self.apply_filters(event):
                return
            
            # Aplicar substituições
            await self.apply_replacements(event)
            
            # Executar ações baseadas no tipo de mensagem
            await self.execute_message_actions(event)
            
            # Clonagem se configurada
            await self.handle_cloning(event)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
    
    def should_process_message(self, event) -> bool:
        """Verifica se deve processar a mensagem"""
        # Verificar se leitura está habilitada
        if not self.read_enabled:
            return False
        
        # Verificar filtros de usuário
        user_id = event.sender_id
        if user_id in self.user_filters.get("blocked", []):
            return False
        
        # Verificar filtros de chat
        chat_id = event.chat_id
        if chat_id in self.user_filters.get("blocked_chats", []):
            return False
        
        return True
    
    def apply_filters(self, event) -> bool:
        """Aplica filtros e retorna True se mensagem deve ser bloqueada"""
        message_text = event.message.text or ""
        
        # Filtro por palavras-chave
        if self.keywords and self.contains_keywords(message_text, self.keywords):
            self.log_activity("info", f"Mensagem filtrada por palavra-chave: {message_text[:100]}")
            return True
        
        # Filtro por regex
        for pattern in self.regex_patterns:
            try:
                if re.search(pattern, message_text, re.IGNORECASE):
                    self.log_activity("info", f"Mensagem filtrada por regex: {pattern}")
                    return True
            except re.error:
                logger.warning(f"Regex inválido: {pattern}")
        
        # Filtro por mídia
        if event.message.media:
            media_type = type(event.message.media).__name__
            if media_type in self.media_filters:
                self.log_activity("info", f"Mensagem filtrada por tipo de mídia: {media_type}")
                return True
        
        return False
    
    async def apply_replacements(self, event):
        """Aplica substituições de conteúdo"""
        if not event.message.text:
            return
        
        original_text = event.message.text
        modified_text = original_text
        
        # Substituir termos
        for rule in self.replace_rules:
            old_term = rule.get("old")
            new_term = rule.get("new")
            if old_term and new_term:
                modified_text = modified_text.replace(old_term, new_term)
        
        # Substituir links
        for old_link, new_link in self.link_replacements.items():
            modified_text = modified_text.replace(old_link, new_link)
        
        # Se texto foi modificado, editar mensagem
        if modified_text != original_text:
            try:
                await self.client.edit_message(event.chat_id, event.message.id, modified_text)
                self.log_activity("info", f"Texto substituído: {original_text[:50]} -> {modified_text[:50]}")
            except Exception as e:
                logger.error(f"Erro ao editar mensagem: {e}")
    
    async def execute_message_actions(self, event):
        """Executa ações baseadas na mensagem"""
        message_text = event.message.text or ""
        
        # Ações de resposta automática
        if self.config.get("auto_reply", False):
            await self.send_auto_reply(event)
        
        # Ações de deleção
        if self.should_delete_message(message_text):
            await self.delete_message(event.chat_id, event.message.id)
            self.messages_deleted += 1
    
    async def send_auto_reply(self, event):
        """Envia resposta automática"""
        if not self.write_enabled:
            return
        
        reply_text = self.generate_reply(event)
        if reply_text:
            await self.send_message(event.chat_id, reply_text, reply_to=event.message.id)
            self.messages_sent += 1
    
    def generate_reply(self, event) -> str:
        """Gera resposta automática"""
        message_text = event.message.text or ""
        
        # Respostas baseadas em palavras-chave
        auto_replies = self.config.get("auto_replies", [])
        for reply_rule in auto_replies:
            keywords = reply_rule.get("keywords", [])
            if keywords and self.contains_keywords(message_text, keywords):
                responses = reply_rule.get("responses", [])
                if responses:
                    import random
                    return random.choice(responses)
        
        return ""
    
    def should_delete_message(self, message_text: str) -> bool:
        """Verifica se deve deletar mensagem"""
        delete_keywords = self.config.get("delete_keywords", [])
        return delete_keywords and self.contains_keywords(message_text, delete_keywords)
    
    async def handle_cloning(self, event):
        """Manipula clonagem de mensagens"""
        if not self.clone_rules:
            return
        
        for rule in self.clone_rules:
            source_chat = rule.get("source_chat")
            target_chat = rule.get("target_chat")
            
            if event.chat_id == source_chat and target_chat:
                await self.clone_message(event, target_chat, rule)
    
    async def clone_message(self, event, target_chat: int, rule: Dict):
        """Clona mensagem para outro chat"""
        try:
            message_text = event.message.text or ""
            
            # Aplicar substituições durante clonagem
            cloned_text = message_text
            clone_replacements = rule.get("replacements", [])
            for replacement in clone_replacements:
                old_term = replacement.get("old")
                new_term = replacement.get("new")
                if old_term and new_term:
                    cloned_text = cloned_text.replace(old_term, new_term)
            
            # Enviar mensagem clonada
            if cloned_text:
                await self.send_message(target_chat, cloned_text)
                self.messages_sent += 1
                self.log_activity("info", f"Mensagem clonada para {target_chat}")
            
            # Clonar mídia se existir
            if event.message.media and self.media_enabled:
                await self.client.send_message(target_chat, file=event.message.media)
                
        except Exception as e:
            logger.error(f"Erro ao clonar mensagem: {e}")
    
    # ===== FUNCIONALIDADES SENSÍVEIS (COM AVISOS) =====
    
    async def add_member(self, chat_id: int, user_id: int) -> bool:
        """Adiciona membro ao chat (FUNCIONALIDADE SENSÍVEL)"""
        try:
            self.log_activity("warning", f"⚠️ TENTATIVA DE ADICIONAR MEMBRO {user_id} AO CHAT {chat_id}")
            
            if not self.member_management.get("add_members", False):
                self.log_activity("error", "❌ Adição de membros desabilitada por segurança")
                return False
            
            # Verificar permissões
            if not await self.has_admin_permissions(chat_id):
                self.log_activity("error", "❌ Sem permissões de admin para adicionar membros")
                return False
            
            await self.client(InviteToChannelRequest(chat_id, [user_id]))
            self.members_managed += 1
            self.log_activity("warning", f"✅ Membro {user_id} adicionado ao chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar membro: {e}")
            self.log_activity("error", f"❌ Erro ao adicionar membro: {e}")
            return False
    
    async def remove_member(self, chat_id: int, user_id: int) -> bool:
        """Remove membro do chat (FUNCIONALIDADE SENSÍVEL)"""
        try:
            self.log_activity("warning", f"⚠️ TENTATIVA DE REMOVER MEMBRO {user_id} DO CHAT {chat_id}")
            
            if not self.member_management.get("remove_members", False):
                self.log_activity("error", "❌ Remoção de membros desabilitada por segurança")
                return False
            
            # Verificar permissões
            if not await self.has_admin_permissions(chat_id):
                self.log_activity("error", "❌ Sem permissões de admin para remover membros")
                return False
            
            await self.client(EditBannedRequest(chat_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            self.members_managed += 1
            self.log_activity("warning", f"✅ Membro {user_id} removido do chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover membro: {e}")
            self.log_activity("error", f"❌ Erro ao remover membro: {e}")
            return False
    
    async def create_group(self, title: str, users: List[int] = None) -> Optional[int]:
        """Cria grupo (FUNCIONALIDADE SENSÍVEL)"""
        try:
            self.log_activity("warning", f"⚠️ TENTATIVA DE CRIAR GRUPO: {title}")
            
            if not self.chat_management.get("create_groups", False):
                self.log_activity("error", "❌ Criação de grupos desabilitada por segurança")
                return None
            
            result = await self.client(CreateChatRequest(users or [], title))
            chat_id = result.chats[0].id
            self.log_activity("warning", f"✅ Grupo criado: {title} (ID: {chat_id})")
            return chat_id
            
        except Exception as e:
            logger.error(f"Erro ao criar grupo: {e}")
            self.log_activity("error", f"❌ Erro ao criar grupo: {e}")
            return None
    
    async def create_channel(self, title: str, description: str = "") -> Optional[int]:
        """Cria canal (FUNCIONALIDADE SENSÍVEL)"""
        try:
            self.log_activity("warning", f"⚠️ TENTATIVA DE CRIAR CANAL: {title}")
            
            if not self.chat_management.get("create_channels", False):
                self.log_activity("error", "❌ Criação de canais desabilitada por segurança")
                return None
            
            result = await self.client(CreateChannelRequest(title, description, megagroup=False))
            channel_id = result.chats[0].id
            self.log_activity("warning", f"✅ Canal criado: {title} (ID: {channel_id})")
            return channel_id
            
        except Exception as e:
            logger.error(f"Erro ao criar canal: {e}")
            self.log_activity("error", f"❌ Erro ao criar canal: {e}")
            return None
    
    # ===== SISTEMA DE STREAMING/CANAL TV =====
    
    async def update_streaming_content(self, channel_id: int, content: str):
        """Atualiza conteúdo de streaming (como canal TV)"""
        try:
            if not self.streaming_config.get("enabled", False):
                return
            
            # Deletar mensagem anterior se configurado
            if self.streaming_config.get("replace_previous", True):
                await self.delete_old_streaming_messages(channel_id)
            
            # Enviar novo conteúdo
            await self.send_message(channel_id, content)
            self.messages_sent += 1
            
            self.log_activity("info", f"Conteúdo de streaming atualizado no canal {channel_id}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar conteúdo de streaming: {e}")
    
    async def delete_old_streaming_messages(self, channel_id: int):
        """Deleta mensagens antigas do streaming"""
        try:
            # Implementar lógica para deletar mensagens antigas
            # baseado na configuração de streaming
            pass
        except Exception as e:
            logger.error(f"Erro ao deletar mensagens antigas: {e}")
    
    # ===== FUNCIONALIDADES AUXILIARES =====
    
    async def has_admin_permissions(self, chat_id: int) -> bool:
        """Verifica se tem permissões de admin"""
        try:
            me = await self.client.get_me()
            participant = await self.client.get_participants(chat_id, filter=lambda x: x.id == me.id)
            return participant and hasattr(participant[0], 'admin_rights')
        except:
            return False
    
    async def get_chat_members(self, chat_id: int) -> List[Dict]:
        """Obtém lista de membros do chat"""
        try:
            participants = await self.client.get_participants(chat_id)
            return [
                {
                    "id": p.id,
                    "username": p.username,
                    "first_name": p.first_name,
                    "last_name": p.last_name
                }
                for p in participants
            ]
        except Exception as e:
            logger.error(f"Erro ao obter membros: {e}")
            return []
    
    # ===== SISTEMA DE LISTAGEM DE CHATS =====
    
    async def get_all_chats(self) -> List[Dict]:
        """Obtém lista de todos os chats acessíveis"""
        try:
            chats = []
            
            # Obter diálogos (chats recentes)
            async for dialog in self.client.iter_dialogs():
                chat_info = await self.get_chat_info(dialog.id)
                if chat_info:
                    chat_info.update({
                        "unread_count": dialog.unread_count,
                        "last_message_date": dialog.date.isoformat() if dialog.date else None,
                        "is_pinned": dialog.is_pinned,
                        "is_archived": dialog.is_archived
                    })
                    chats.append(chat_info)
            
            return chats
            
        except Exception as e:
            logger.error(f"Erro ao obter chats: {e}")
            return []
    
    async def get_groups(self) -> List[Dict]:
        """Obtém lista de grupos"""
        try:
            groups = []
            
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group:
                    chat_info = await self.get_chat_info(dialog.id)
                    if chat_info:
                        chat_info.update({
                            "type": "group",
                            "unread_count": dialog.unread_count,
                            "last_message_date": dialog.date.isoformat() if dialog.date else None,
                            "is_pinned": dialog.is_pinned,
                            "is_archived": dialog.is_archived
                        })
                        groups.append(chat_info)
            
            return groups
            
        except Exception as e:
            logger.error(f"Erro ao obter grupos: {e}")
            return []
    
    async def get_channels(self) -> List[Dict]:
        """Obtém lista de canais"""
        try:
            channels = []
            
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel:
                    chat_info = await self.get_chat_info(dialog.id)
                    if chat_info:
                        chat_info.update({
                            "type": "channel",
                            "unread_count": dialog.unread_count,
                            "last_message_date": dialog.date.isoformat() if dialog.date else None,
                            "is_pinned": dialog.is_pinned,
                            "is_archived": dialog.is_archived
                        })
                        channels.append(chat_info)
            
            return channels
            
        except Exception as e:
            logger.error(f"Erro ao obter canais: {e}")
            return []
    
    async def get_private_chats(self) -> List[Dict]:
        """Obtém lista de chats privados"""
        try:
            private_chats = []
            
            async for dialog in self.client.iter_dialogs():
                if dialog.is_user:
                    chat_info = await self.get_chat_info(dialog.id)
                    if chat_info:
                        chat_info.update({
                            "type": "private",
                            "unread_count": dialog.unread_count,
                            "last_message_date": dialog.date.isoformat() if dialog.date else None,
                            "is_pinned": dialog.is_pinned,
                            "is_archived": dialog.is_archived
                        })
                        private_chats.append(chat_info)
            
            return private_chats
            
        except Exception as e:
            logger.error(f"Erro ao obter chats privados: {e}")
            return []
    
    async def search_chats(self, query: str) -> List[Dict]:
        """Busca chats por nome ou username"""
        try:
            results = []
            
            # Buscar em todos os chats
            all_chats = await self.get_all_chats()
            
            query_lower = query.lower()
            for chat in all_chats:
                # Buscar por título
                if chat.get("title") and query_lower in chat["title"].lower():
                    results.append(chat)
                # Buscar por username
                elif chat.get("username") and query_lower in chat["username"].lower():
                    results.append(chat)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar chats: {e}")
            return []
    
    async def get_chat_by_id(self, chat_id: int) -> Optional[Dict]:
        """Obtém informações de um chat específico por ID"""
        try:
            entity = await self.client.get_entity(chat_id)
            return await self.get_chat_info(chat_id)
        except Exception as e:
            logger.error(f"Erro ao obter chat {chat_id}: {e}")
            return None
    
    async def get_chat_by_username(self, username: str) -> Optional[Dict]:
        """Obtém informações de um chat por username"""
        try:
            entity = await self.client.get_entity(username)
            return await self.get_chat_info(entity.id)
        except Exception as e:
            logger.error(f"Erro ao obter chat @{username}: {e}")
            return None
    
    async def get_chat_statistics(self, chat_id: int) -> Dict:
        """Obtém estatísticas de um chat"""
        try:
            # Informações básicas
            chat_info = await self.get_chat_info(chat_id)
            if not chat_info:
                return {}
            
            # Contar membros
            member_count = 0
            try:
                participants = await self.client.get_participants(chat_id)
                member_count = len(participants)
            except:
                pass
            
            # Obter mensagens recentes
            recent_messages = []
            try:
                async for message in self.client.iter_messages(chat_id, limit=10):
                    recent_messages.append({
                        "id": message.id,
                        "text": message.text[:100] if message.text else "",
                        "date": message.date.isoformat(),
                        "sender_id": message.sender_id
                    })
            except:
                pass
            
            return {
                "chat_info": chat_info,
                "member_count": member_count,
                "recent_messages": recent_messages,
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do chat {chat_id}: {e}")
            return {}
    
    async def export_chat_list(self, file_path: str = None) -> str:
        """Exporta lista de chats para arquivo JSON"""
        try:
            if not file_path:
                file_path = f"/app/exports/chat_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Criar diretório se não existir
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Obter todos os chats
            all_chats = await self.get_all_chats()
            
            # Salvar em arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_chats, f, indent=2, ensure_ascii=False)
            
            self.log_activity("info", f"Lista de chats exportada para: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Erro ao exportar lista de chats: {e}")
            return ""
    
    async def import_chat_list(self, file_path: str) -> List[Dict]:
        """Importa lista de chats de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chats = json.load(f)
            
            self.log_activity("info", f"Lista de chats importada de: {file_path}")
            return chats
            
        except Exception as e:
            logger.error(f"Erro ao importar lista de chats: {e}")
            return []
    
    async def run_bot_logic(self):
        """Lógica principal do bot avançado"""
        await super().run_bot_logic()
        
        # Lógica de streaming
        if self.streaming_config.get("enabled", False):
            await self.run_streaming_logic()
        
        # Lógica de mensagens agendadas
        if self.scheduled_messages:
            await self.run_scheduler_logic()
    
    async def run_streaming_logic(self):
        """Executa lógica de streaming"""
        while self.running:
            try:
                # Atualizar conteúdo de streaming
                for channel_config in self.streaming_config.get("channels", []):
                    channel_id = channel_config.get("channel_id")
                    content = channel_config.get("content")
                    
                    if channel_id and content:
                        await self.update_streaming_content(channel_id, content)
                
                # Aguardar intervalo configurado
                interval = self.streaming_config.get("update_interval", 300)  # 5 minutos
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro na lógica de streaming: {e}")
                await asyncio.sleep(60)
    
    async def run_scheduler_logic(self):
        """Executa lógica de agendamento"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for message in self.scheduled_messages:
                    if self.should_send_scheduled_message(message, current_time):
                        await self.send_scheduled_message(message)
                
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na lógica de agendamento: {e}")
                await asyncio.sleep(60)
    
    def should_send_scheduled_message(self, message: Dict, current_time: datetime) -> bool:
        """Verifica se deve enviar mensagem agendada"""
        # Implementar lógica de agendamento
        return False
    
    async def send_scheduled_message(self, message: Dict):
        """Envia mensagem agendada"""
        try:
            chat_id = message.get("chat_id")
            text = message.get("text")
            
            if chat_id and text:
                await self.send_message(chat_id, text)
                self.messages_sent += 1
                self.log_activity("info", f"Mensagem agendada enviada para {chat_id}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem agendada: {e}")

if __name__ == "__main__":
    import os
    
    bot_name = os.getenv("BOT_NAME", "advanced_bot")
    phone_number = os.getenv("PHONE_NUMBER", "")
    
    if not phone_number:
        logger.error("PHONE_NUMBER não definido")
        exit(1)
    
    bot = AdvancedBot(bot_name, phone_number)
    asyncio.run(bot.start())
