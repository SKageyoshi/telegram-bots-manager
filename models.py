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
    
    def __repr__(self):
        return f"<Bot(name='{self.name}', type='{self.bot_type}', status='{self.status}')>"

class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})
    
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
