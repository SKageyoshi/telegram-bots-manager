from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./telegram_bots.db")

# Criar engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Criar sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Criar todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Inicializar banco de dados com dados de exemplo"""
    create_tables()
    
    # Adicionar dados de exemplo se não existirem
    db = SessionLocal()
    try:
        from models import Bot
        
        # Verificar se já existem bots
        if db.query(Bot).count() == 0:
            # Criar bot de exemplo
            example_bot = Bot(
                name="Bot de Exemplo",
                description="Bot de demonstração do sistema",
                bot_type="responder",
                token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                status="inactive",
                config={
                    "keywords": ["oi", "olá", "hello"],
                    "responses": ["Olá! Como posso ajudar?", "Oi! Tudo bem?"],
                    "delay": 1
                }
            )
            db.add(example_bot)
            db.commit()
            print("✅ Banco de dados inicializado com dados de exemplo")
        else:
            print("✅ Banco de dados já inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        db.rollback()
    finally:
        db.close()
