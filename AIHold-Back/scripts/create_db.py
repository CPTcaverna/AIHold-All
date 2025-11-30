"""
Script auxiliar para criar banco de dados PostgreSQL
Execute: python scripts/create_db.py
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Cria o banco de dados e usuário se não existirem"""
    
    # Obter configurações do .env ou usar padrões
    db_url = os.getenv("DATABASE_URL", "")
    
    if not db_url or not db_url.startswith("postgresql"):
        print("⚠️  DATABASE_URL não configurado ou não é PostgreSQL")
        print("\nConfigure no arquivo .env:")
        print("DATABASE_URL=postgresql://postgres:senha@localhost:5432/aihold_db")
        return
    
    # Extrair informações da URL
    # Formato: postgresql://user:password@host:port/database
    try:
        # Remover postgresql://
        url_parts = db_url.replace("postgresql://", "").split("@")
        if len(url_parts) != 2:
            raise ValueError("Formato inválido")
        
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        if len(host_db) < 2:
            raise ValueError("Formato inválido")
        
        db_name = host_db[1].split("?")[0]  # Remove query parameters
        host_port = host_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        print(f"📊 Conectando ao PostgreSQL...")
        print(f"   Host: {host}:{port}")
        print(f"   Usuário: {user}")
        print(f"   Banco: {db_name}")
        
        # Conectar ao PostgreSQL (banco padrão 'postgres')
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # Conecta ao banco padrão
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar se o banco existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Banco de dados '{db_name}' já existe")
        else:
            print(f"📦 Criando banco de dados '{db_name}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"✅ Banco de dados '{db_name}' criado com sucesso!")
        
        cursor.close()
        conn.close()
        
        # Testar conexão ao banco criado
        print(f"\n🔍 Testando conexão ao banco '{db_name}'...")
        test_conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        test_conn.close()
        print(f"✅ Conexão bem-sucedida!")
        
        print("\n🎉 Configuração concluída!")
        print(f"\n📝 Próximos passos:")
        print(f"   1. Execute: uvicorn main:app --reload")
        print(f"   2. As tabelas serão criadas automaticamente")
        print(f"   3. Use: python scripts/init_db.py para criar dados de exemplo")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\n💡 Verifique:")
        print("   - PostgreSQL está rodando?")
        print("   - Credenciais estão corretas no .env?")
        print("   - Host e porta estão corretos?")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Verifique o formato da DATABASE_URL no arquivo .env")
        print("   Formato esperado: postgresql://usuario:senha@host:porta/banco")


if __name__ == "__main__":
    create_database()



