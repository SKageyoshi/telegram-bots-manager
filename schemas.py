from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BotType(str, Enum):
    RESPONDER = "responder"
    DELETER = "deleter"
    MONITOR = "monitor"
    SCHEDULER = "scheduler"
    ADVANCED = "advanced"

class BotStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class BotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nome do bot")
    description: Optional[str] = Field(None, description="Descrição do bot")
    bot_type: BotType = Field(..., description="Tipo do bot")
    token: str = Field(..., min_length=10, description="Token do bot do Telegram")
    config: Optional[Dict[str, Any]] = Field(default={}, description="Configurações específicas do bot")
    
    # Campos de autenticação Telegram
    api_id: Optional[str] = Field(None, description="API ID do Telegram")
    api_hash: Optional[str] = Field(None, description="API Hash do Telegram")
    phone_number: Optional[str] = Field(None, description="Número de telefone")

class BotCreate(BotBase):
    pass

class BotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    bot_type: Optional[BotType] = None
    token: Optional[str] = Field(None, min_length=10)
    status: Optional[BotStatus] = None
    config: Optional[Dict[str, Any]] = None
    api_id: Optional[str] = None
    api_hash: Optional[str] = None
    phone_number: Optional[str] = None
    is_authenticated: Optional[bool] = None
    auth_status: Optional[str] = None

class BotResponse(BotBase):
    id: int
    status: BotStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_messages: int = 0
    last_activity: Optional[datetime] = None
    is_authenticated: bool = False
    auth_status: str = "pending"
    
    class Config:
        from_attributes = True

class BotList(BaseModel):
    id: int
    name: str
    bot_type: BotType
    status: BotStatus
    total_messages: int
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BotStats(BaseModel):
    total_bots: int
    active_bots: int
    total_messages: int
    uptime: str

class BotLogCreate(BaseModel):
    bot_id: int
    level: str = Field(..., regex="^(info|warning|error|debug)$")
    message: str
    metadata: Optional[Dict[str, Any]] = {}

class BotLogResponse(BaseModel):
    id: int
    bot_id: int
    level: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True

# Schemas para configurações específicas de cada tipo de bot

class ResponderBotConfig(BaseModel):
    keywords: list[str] = Field(default=[], description="Palavras-chave para ativar resposta")
    responses: list[str] = Field(default=[], description="Respostas possíveis")
    delay: int = Field(default=1, ge=0, le=60, description="Delay entre respostas em segundos")
    mode: str = Field(default="first", regex="^(first|random|all)$", description="Modo de resposta")
    groups: list[str] = Field(default=[], description="IDs dos grupos permitidos")
    users: list[str] = Field(default=[], description="IDs dos usuários permitidos")

class DeleterBotConfig(BaseModel):
    delete_keywords: list[str] = Field(default=[], description="Palavras-chave para deletar")
    delete_users: list[str] = Field(default=[], description="IDs de usuários para deletar mensagens")
    delete_after_hours: int = Field(default=24, ge=1, le=168, description="Deletar mensagens após X horas")
    protected_users: list[str] = Field(default=[], description="Usuários protegidos")
    silent_mode: bool = Field(default=True, description="Modo silencioso")
    groups: list[str] = Field(default=[], description="IDs dos grupos permitidos")

class MonitorBotConfig(BaseModel):
    monitor_groups: list[str] = Field(default=[], description="Grupos para monitorar")
    alert_keywords: list[str] = Field(default=[], description="Palavras-chave para alertas")
    alert_users: list[str] = Field(default=[], description="Usuários para receber alertas")
    backup_messages: bool = Field(default=False, description="Fazer backup das mensagens")
    sentiment_analysis: bool = Field(default=False, description="Análise de sentimentos")
    report_frequency: str = Field(default="daily", regex="^(hourly|daily|weekly)$", description="Frequência dos relatórios")

class SchedulerBotConfig(BaseModel):
    tasks: list[Dict[str, Any]] = Field(default=[], description="Lista de tarefas agendadas")
    timezone: str = Field(default="America/Sao_Paulo", description="Fuso horário")
    max_tasks: int = Field(default=10, ge=1, le=100, description="Máximo de tarefas")
    groups: list[str] = Field(default=[], description="IDs dos grupos para envio")
    users: list[str] = Field(default=[], description="IDs dos usuários para envio")

class AdvancedBotConfig(BaseModel):
    webhook_url: Optional[str] = Field(None, description="URL do webhook")
    api_key: Optional[str] = Field(None, description="Chave da API")
    integrations: Dict[str, Any] = Field(default={}, description="Integrações externas")
    custom_commands: list[Dict[str, Any]] = Field(default=[], description="Comandos customizados")
    machine_learning: bool = Field(default=False, description="Habilitar Machine Learning")
    groups: list[str] = Field(default=[], description="IDs dos grupos permitidos")
    users: list[str] = Field(default=[], description="IDs dos usuários permitidos")
