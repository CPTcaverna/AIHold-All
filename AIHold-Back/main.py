from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, ativos, configuracoes, carteira, investimentos
from app.database import engine, Base
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIHold API",
    description="API para gerenciamento de carteira de investimentos com algoritmos de otimização",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(ativos.router, prefix="/api/ativos", tags=["Ativos"])
app.include_router(configuracoes.router, prefix="/api/configuracoes", tags=["Configurações"])
app.include_router(carteira.router, prefix="/api/carteira", tags=["Carteira"])
app.include_router(investimentos.router, prefix="/api/investimentos", tags=["Investimentos"])


@app.get("/")
async def root():
    return {"message": "Bem-vindo à API AIHold", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

