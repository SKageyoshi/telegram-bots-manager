from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Importar módulos locais
from database import get_db, init_database
from models import Bot, BotLog, BotStats, TelegramSession, User, UserTelegramAccount
from schemas import BotCreate, BotUpdate, BotResponse, BotList, BotStats as BotStatsSchema
from telegram_service import get_telegram_service

app = FastAPI(title="Telegram Bots Manager", version="1.2.0")

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar banco de dados
init_database()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Telegram Bots Manager",
        "version": "1.2.0"
    })

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API ENDPOINTS

@app.get("/api/bots", response_model=List[BotList])
def get_bots(db: Session = Depends(get_db)):
    """Obter lista de todos os bots"""
    bots = db.query(Bot).all()
    return bots

@app.get("/api/bots/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: int, db: Session = Depends(get_db)):
    """Obter bot específico por ID"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    return bot

@app.post("/api/bots", response_model=BotResponse)
def create_bot(bot: BotCreate, db: Session = Depends(get_db)):
    """Criar novo bot"""
    # Verificar se já existe bot com mesmo nome ou token
    existing_bot = db.query(Bot).filter(
        (Bot.name == bot.name) | (Bot.token == bot.token)
    ).first()
    
    if existing_bot:
        if existing_bot.name == bot.name:
            raise HTTPException(status_code=400, detail="Já existe um bot com este nome")
        else:
            raise HTTPException(status_code=400, detail="Já existe um bot com este token")
    
        # Criar novo bot
        db_bot = Bot(
            name=bot.name,
            description=bot.description,
            bot_type=bot.bot_type,
            token=bot.token,
            config=bot.config or {},
            api_id=bot.api_id,
            api_hash=bot.api_hash,
            phone_number=bot.phone_number
        )
    
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    
    return db_bot

@app.put("/api/bots/{bot_id}", response_model=BotResponse)
def update_bot(bot_id: int, bot_update: BotUpdate, db: Session = Depends(get_db)):
    """Atualizar bot existente"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    # Atualizar campos fornecidos
    update_data = bot_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)
    
    db.commit()
    db.refresh(bot)
    
    return bot

@app.delete("/api/bots/{bot_id}")
def delete_bot(bot_id: int, db: Session = Depends(get_db)):
    """Deletar bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    db.delete(bot)
    db.commit()
    
    return {"message": "Bot deletado com sucesso"}

@app.get("/api/stats", response_model=BotStatsSchema)
def get_stats(db: Session = Depends(get_db)):
    """Obter estatísticas gerais"""
    total_bots = db.query(Bot).count()
    active_bots = db.query(Bot).filter(Bot.status == "active").count()
    total_messages = db.query(Bot).with_entities(Bot.total_messages).all()
    total_messages_sum = sum(msg[0] for msg in total_messages)
    
    return {
        "total_bots": total_bots,
        "active_bots": active_bots,
        "total_messages": total_messages_sum,
        "uptime": "99.9%"
    }

@app.post("/api/bots/{bot_id}/start")
def start_bot(bot_id: int, db: Session = Depends(get_db)):
    """Iniciar bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    bot.status = "active"
    db.commit()
    
    return {"message": f"Bot {bot.name} iniciado com sucesso"}

@app.post("/api/bots/{bot_id}/stop")
def stop_bot(bot_id: int, db: Session = Depends(get_db)):
    """Parar bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    bot.status = "inactive"
    db.commit()
    
    return {"message": f"Bot {bot.name} parado com sucesso"}

# NOVAS APIs DE AUTENTICAÇÃO TELEGRAM

@app.post("/api/bots/{bot_id}/send-code")
async def send_telegram_code(bot_id: int, phone_number: str, db: Session = Depends(get_db)):
    """Enviar código SMS para autenticação"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    if not bot.api_id or not bot.api_hash:
        raise HTTPException(status_code=400, detail="API ID e API Hash são necessários")
    
    try:
        telegram_service = get_telegram_service()
        result = await telegram_service.send_code(bot, phone_number)
        
        if result["success"]:
            bot.phone_number = phone_number
            bot.auth_status = "code_sent"
            db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar código: {str(e)}")

@app.post("/api/bots/{bot_id}/authenticate")
async def authenticate_bot(bot_id: int, code: str, password: str = None, db: Session = Depends(get_db)):
    """Autenticar bot com código SMS e senha 2FA"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    if not bot.phone_number:
        raise HTTPException(status_code=400, detail="Número de telefone não configurado")
    
    try:
        telegram_service = get_telegram_service()
        result = await telegram_service.authenticate_bot(bot, bot.phone_number, code, password)
        
        if result["success"]:
            db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na autenticação: {str(e)}")

@app.get("/api/bots/{bot_id}/test-connection")
async def test_bot_connection(bot_id: int, db: Session = Depends(get_db)):
    """Testar conexão do bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    
    try:
        telegram_service = get_telegram_service()
        result = await telegram_service.test_connection(bot)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")

# APIs DE CONTAS TELEGRAM

@app.get("/api/accounts")
def get_accounts(db: Session = Depends(get_db)):
    """Obter lista de contas Telegram"""
    accounts = db.query(UserTelegramAccount).all()
    return accounts

@app.post("/api/accounts")
def create_account(account_data: dict, db: Session = Depends(get_db)):
    """Criar nova conta Telegram"""
    phone_number = account_data.get('phone_number')
    api_id = account_data.get('api_id')
    api_hash = account_data.get('api_hash')
    
    if not phone_number or not api_id or not api_hash:
        raise HTTPException(status_code=400, detail="phone_number, api_id e api_hash são obrigatórios")
    
    # Verificar se já existe conta com mesmo número
    existing_account = db.query(UserTelegramAccount).filter(
        UserTelegramAccount.phone_number == phone_number
    ).first()
    
    if existing_account:
        raise HTTPException(status_code=400, detail="Já existe uma conta com este número")
    
    # Criar nova conta
    db_account = UserTelegramAccount(
        user_id=1,  # Por enquanto, usuário padrão
        phone_number=phone_number,
        api_id=api_id,
        api_hash=api_hash
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account

@app.get("/api/accounts/{account_id}/test-connection")
async def test_account_connection(account_id: int, db: Session = Depends(get_db)):
    """Testar conexão da conta"""
    account = db.query(UserTelegramAccount).filter(UserTelegramAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    try:
        telegram_service = get_telegram_service()
        result = await telegram_service.test_connection(account)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Deletar conta"""
    account = db.query(UserTelegramAccount).filter(UserTelegramAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    db.delete(account)
    db.commit()
    
    return {"message": "Conta deletada com sucesso"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
