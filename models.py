from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    bot_type = Column(String(50), nullable=False)  # responder, deleter, monitor, scheduler, advanced
    token = Column(String(200), nullable=False, unique=True)
    status = Column(String(20), default="inactive")  # active, inactive, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configurações específicas do bot
    config = Column(JSON, default={})
    
    # Estatísticas
    total_messages = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Campos de autenticação Telegram
    api_id = Column(String(50), nullable=True)
    api_hash = Column(String(200), nullable=True)
    phone_number = Column(String(20), nullable=True)
    session_string = Column(Text, nullable=True)  # Sessão serializada
    is_authenticated = Column(Boolean, default=False)
    auth_status = Column(String(20), default="pending")  # pending, authenticated, error
    
    def __repr__(self):
        return f"<Bot(name='{self.name}', type='{self.bot_type}', status='{self.status}')>"

class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    log_data = Column(JSON, default={})  # Renomeado de 'metadata' para 'log_data'
    
    def __repr__(self):
        return f"<BotLog(bot_id={self.bot_id}, level='{self.level}', message='{self.message[:50]}...')>"

class BotStats(Base):
    __tablename__ = "bot_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    messages_processed = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    uptime_seconds = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<BotStats(bot_id={self.bot_id}, messages={self.messages_processed}, errors={self.errors_count})>"

class TelegramSession(Base):
    __tablename__ = "telegram_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, nullable=False)
    phone_number = Column(String(20), nullable=False)
    session_data = Column(Text, nullable=False)  # Dados da sessão Telethon
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    phone_number = Column(String(20), nullable=True, unique=True)
    password_hash = Column(String(255), nullable=True)  # Para autenticação local
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Configurações do usuário
    preferences = Column(JSON, default={})
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class UserTelegramAccount(Base):
    __tablename__ = "user_telegram_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    phone_number = Column(String(20), nullable=False)
    api_id = Column(String(50), nullable=False)
    api_hash = Column(String(200), nullable=False)
    session_string = Column(Text, nullable=True)
    is_authenticated = Column(Boolean, default=False)
    auth_status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserTelegramAccount(user_id={self.user_id}, phone='{self.phone_number}')>"
