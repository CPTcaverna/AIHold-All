from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    ativos = relationship("Ativo", back_populates="user", cascade="all, delete-orphan")
    configuracoes = relationship("Configuracao", back_populates="user", uselist=False, cascade="all, delete-orphan")
    carteira = relationship("Carteira", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Ativo(Base):
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'acao' ou 'fii'
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, default=0, nullable=False)
    porcentagem_ideal = Column(Float, default=0.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="ativos")

    # Índice composto para melhor performance em queries por usuário e código
    __table_args__ = (
        Index('idx_ativo_user_codigo', 'user_id', 'codigo'),
    )

    def __repr__(self):
        return f"<Ativo {self.codigo} - {self.nome}>"


class Configuracao(Base):
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True, index=True)
    porcentagem_acoes = Column(Float, default=50.0, nullable=False)
    porcentagem_fii = Column(Float, default=50.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="configuracoes")

    def __repr__(self):
        return f"<Configuracao User {self.user_id} - Ações: {self.porcentagem_acoes}%, FIIs: {self.porcentagem_fii}%>"


class Carteira(Base):
    __tablename__ = "carteira"

    id = Column(Integer, primary_key=True, index=True)
    valor_total = Column(Float, default=0.0, nullable=False)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="carteira")

    def __repr__(self):
        return f"<Carteira User {self.user_id} - Valor: R$ {self.valor_total}>"

