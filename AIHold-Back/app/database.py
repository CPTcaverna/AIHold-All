from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
# Suporta SQLite (padrão) e PostgreSQL
# Para PostgreSQL, use: DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aihold.db")

# Configurar engine baseado no tipo de banco
if DATABASE_URL.startswith("sqlite"):
    # SQLite
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Mude para True para ver SQL queries
    )
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_size=5,  # Tamanho do pool de conexões
        max_overflow=10,  # Máximo de conexões extras
        echo=False  # Mude para True para ver SQL queries
    )
else:
    # Outros bancos (MySQL, etc)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

