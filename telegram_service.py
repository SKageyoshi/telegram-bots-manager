import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.tl.types import User
from sqlalchemy.orm import Session
from models import Bot, TelegramSession
import json
import os

logger = logging.getLogger(__name__)

class TelegramAuthService:
    def __init__(self, api_id: str, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
    
    async def authenticate_bot(self, bot: Bot, phone_number: str, code: str = None, password: str = None) -> dict:
        """
        Autentica um bot do Telegram
        
        Args:
            bot: Instância do bot
            phone_number: Número de telefone
            code: Código SMS (se necessário)
            password: Senha 2FA (se necessário)
        
        Returns:
            dict: Resultado da autenticação
        """
        try:
            # Criar cliente Telethon
            client = TelegramClient(
                f'session_{bot.id}',
                self.api_id,
                self.api_hash
            )
            
            await client.start(
                phone=phone_number,
                code_callback=lambda: code,
                password=password
            )
            
            # Verificar se está autenticado
            if await client.is_user_authorized():
                # Obter informações do usuário
                me = await client.get_me()
                
                # Serializar sessão
                session_string = client.session.save()
                
                # Atualizar bot no banco
                bot.is_authenticated = True
                bot.auth_status = "authenticated"
                bot.phone_number = phone_number
                bot.session_string = session_string
                
                # Salvar sessão
                await self.save_session(bot.id, phone_number, session_string)
                
                await client.disconnect()
                
                return {
                    "success": True,
                    "message": f"Bot autenticado com sucesso! Usuário: {me.first_name}",
                    "user_info": {
                        "id": me.id,
                        "first_name": me.first_name,
                        "username": me.username,
                        "phone": me.phone
                    }
                }
            else:
                await client.disconnect()
                return {
                    "success": False,
                    "message": "Falha na autenticação",
                    "error": "Não foi possível autenticar"
                }
                
        except SessionPasswordNeededError:
            return {
                "success": False,
                "message": "Senha 2FA necessária",
                "error": "2FA_REQUIRED"
            }
        except PhoneCodeInvalidError:
            return {
                "success": False,
                "message": "Código SMS inválido",
                "error": "INVALID_CODE"
            }
        except Exception as e:
            logger.error(f"Erro na autenticação do bot {bot.id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro na autenticação: {str(e)}",
                "error": str(e)
            }
    
    async def send_code(self, bot: Bot, phone_number: str) -> dict:
        """
        Envia código SMS para o número
        
        Args:
            bot: Instância do bot
            phone_number: Número de telefone
        
        Returns:
            dict: Resultado do envio
        """
        try:
            client = TelegramClient(
                f'session_{bot.id}',
                self.api_id,
                self.api_hash
            )
            
            await client.connect()
            
            # Enviar código
            await client.send_code_request(phone_number)
            
            await client.disconnect()
            
            return {
                "success": True,
                "message": "Código SMS enviado com sucesso!"
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar código para {phone_number}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao enviar código: {str(e)}",
                "error": str(e)
            }
    
    async def save_session(self, bot_id: int, phone_number: str, session_data: str):
        """
        Salva sessão no banco de dados
        """
        # Esta função será implementada quando tivermos acesso ao banco
        pass
    
    async def load_session(self, bot_id: int) -> TelegramClient:
        """
        Carrega sessão do banco de dados
        
        Args:
            bot_id: ID do bot
        
        Returns:
            TelegramClient: Cliente autenticado
        """
        try:
            # Buscar sessão no banco
            # session = db.query(TelegramSession).filter(TelegramSession.bot_id == bot_id).first()
            
            # Por enquanto, criar cliente básico
            client = TelegramClient(
                f'session_{bot_id}',
                self.api_id,
                self.api_hash
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                return client
            else:
                await client.disconnect()
                return None
                
        except Exception as e:
            logger.error(f"Erro ao carregar sessão do bot {bot_id}: {str(e)}")
            return None
    
    async def test_connection(self, bot: Bot) -> dict:
        """
        Testa conexão do bot
        
        Args:
            bot: Instância do bot
        
        Returns:
            dict: Resultado do teste
        """
        try:
            client = await self.load_session(bot.id)
            
            if client:
                me = await client.get_me()
                await client.disconnect()
                
                return {
                    "success": True,
                    "message": f"Conexão OK! Usuário: {me.first_name}",
                    "user_info": {
                        "id": me.id,
                        "first_name": me.first_name,
                        "username": me.username
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Bot não autenticado",
                    "error": "NOT_AUTHENTICATED"
                }
                
        except Exception as e:
            logger.error(f"Erro ao testar conexão do bot {bot.id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro na conexão: {str(e)}",
                "error": str(e)
            }

# Instância global do serviço
telegram_service = None

def get_telegram_service() -> TelegramAuthService:
    """
    Obtém instância do serviço Telegram
    """
    global telegram_service
    if telegram_service is None:
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        
        if not api_id or not api_hash:
            raise ValueError("TELEGRAM_API_ID e TELEGRAM_API_HASH devem estar configurados")
        
        telegram_service = TelegramAuthService(api_id, api_hash)
    
    return telegram_service
