"""
Script para inicializar o banco de dados com dados de exemplo
Execute: python scripts/init_db.py
"""
import sys
import os
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Ativo, Configuracao, Carteira
from app.auth import get_password_hash
import bcrypt

def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt diretamente"""
    try:
        # Tentar usar a função do auth primeiro
        return get_password_hash(password)
    except:
        # Se falhar, usar bcrypt diretamente
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Dados de exemplo
dados_iniciais = [
    {"codigo": "VALE3", "nome": "Vale", "tipo": "acao", "quantidade": 0, "preco": 68.20, "porcentagem_ideal": 16},
    {"codigo": "ITUB4", "nome": "Itaú Unibanco", "tipo": "acao", "quantidade": 0, "preco": 32.15, "porcentagem_ideal": 16},
    {"codigo": "IAJI11", "nome": "IAJI11", "tipo": "acao", "quantidade": 0, "preco": 46.60, "porcentagem_ideal": 17},
    {"codigo": "RETES", "nome": "RETES", "tipo": "acao", "quantidade": 0, "preco": 66.60, "porcentagem_ideal": 17},
    {"codigo": "ABEV3", "nome": "Ambev", "tipo": "acao", "quantidade": 0, "preco": 14.72, "porcentagem_ideal": 17},
    {"codigo": "B3SA3", "nome": "B3", "tipo": "acao", "quantidade": 0, "preco": 12.91, "porcentagem_ideal": 17},
    {"codigo": "BTAL11", "nome": "BTAL11", "tipo": "fii", "quantidade": 0, "preco": 98.70, "porcentagem_ideal": 16},
    {"codigo": "BTLG11", "nome": "BTLG11", "tipo": "fii", "quantidade": 0, "preco": 120.45, "porcentagem_ideal": 16},
    {"codigo": "CPTS11", "nome": "CPTS11", "tipo": "fii", "quantidade": 0, "preco": 104.30, "porcentagem_ideal": 17},
    {"codigo": "DEVA11", "nome": "DEVA11", "tipo": "fii", "quantidade": 0, "preco": 112.50, "porcentagem_ideal": 17},
    {"codigo": "FIIB11", "nome": "FIIB11", "tipo": "fii", "quantidade": 0, "preco": 276.90, "porcentagem_ideal": 17},
    {"codigo": "GTWR11", "nome": "GTWR11", "tipo": "fii", "quantidade": 0, "preco": 87.60, "porcentagem_ideal": 17},
]


def init_db():
    db = SessionLocal()
    
    try:
        # Criar usuário de exemplo
        usuario = db.query(User).filter(User.username == "admin").first()
        if not usuario:
            usuario = User(
                username="admin",
                email="admin@aihold.com",
                hashed_password=hash_password("admin123")
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            print(f"✅ Usuário criado: {usuario.username} (senha: admin123)")
        else:
            print(f"ℹ️  Usuário já existe: {usuario.username}")
        
        # Criar configurações
        config = db.query(Configuracao).filter(Configuracao.user_id == usuario.id).first()
        if not config:
            config = Configuracao(
                user_id=usuario.id,
                porcentagem_acoes=50.0,
                porcentagem_fii=50.0
            )
            db.add(config)
            db.commit()
            print("✅ Configurações criadas")
        else:
            print("ℹ️  Configurações já existem")
        
        # Criar ativos
        ativos_criados = 0
        for dados in dados_iniciais:
            ativo_existente = db.query(Ativo).filter(
                Ativo.codigo == dados["codigo"],
                Ativo.user_id == usuario.id
            ).first()
            
            if not ativo_existente:
                ativo = Ativo(
                    codigo=dados["codigo"],
                    nome=dados["nome"],
                    tipo=dados["tipo"],
                    preco=dados["preco"],
                    quantidade=dados["quantidade"],
                    porcentagem_ideal=dados["porcentagem_ideal"],
                    user_id=usuario.id
                )
                db.add(ativo)
                ativos_criados += 1
        
        db.commit()
        print(f"✅ {ativos_criados} ativos criados")
        
        # Criar carteira
        carteira = db.query(Carteira).filter(Carteira.user_id == usuario.id).first()
        if not carteira:
            valor_total = sum(ativo.preco * ativo.quantidade for ativo in db.query(Ativo).filter(Ativo.user_id == usuario.id).all())
            carteira = Carteira(
                user_id=usuario.id,
                valor_total=valor_total
            )
            db.add(carteira)
            db.commit()
            print("✅ Carteira criada")
        else:
            print("ℹ️  Carteira já existe")
        
        print("\n🎉 Inicialização concluída!")
        print(f"\n📝 Credenciais de teste:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao inicializar banco: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

