from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Importar módulos locais
from database import get_db, init_database
from models import Bot, BotLog, BotStats
from schemas import BotCreate, BotUpdate, BotResponse, BotList, BotStats as BotStatsSchema

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
        config=bot.config or {}
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
