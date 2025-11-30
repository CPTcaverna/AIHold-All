from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List
from datetime import datetime


# Schemas de Autenticação
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Schemas de Ativos
class AtivoBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=20)
    nome: str = Field(..., min_length=1)
    tipo: str = Field(..., pattern="^(acao|fii)$")
    preco: float = Field(..., gt=0)
    quantidade: int = Field(default=0, ge=0)
    porcentagem_ideal: float = Field(default=0.0, ge=0, le=100)


class AtivoCreate(BaseModel):
    """
    Schema para criação de ativo.
    Apenas o código é obrigatório - nome, tipo e preco são opcionais 
    e serão buscados automaticamente na API brapi.dev se não fornecidos.
    """
    codigo: str = Field(..., min_length=1, max_length=20, description="Código do ativo (ex: PETR4, HGLG11)")
    nome: Optional[str] = Field(None, min_length=1, description="Nome do ativo (opcional - será buscado automaticamente)")
    tipo: Optional[str] = Field(None, pattern="^(acao|fii)$", description="Tipo do ativo: 'acao' ou 'fii' (opcional - será detectado automaticamente)")
    preco: Optional[float] = Field(None, gt=0, description="Preço atual do ativo (opcional - será buscado automaticamente)")
    quantidade: int = Field(default=0, ge=0)
    porcentagem_ideal: float = Field(default=0.0, ge=0, le=100)


class AtivoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=1, max_length=20)
    nome: Optional[str] = Field(None, min_length=1)
    tipo: Optional[str] = Field(None, pattern="^(acao|fii)$")
    preco: Optional[float] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, ge=0)
    porcentagem_ideal: Optional[float] = Field(None, ge=0, le=100)


class AtivoResponse(AtivoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Schemas de Configurações
class ConfiguracaoBase(BaseModel):
    porcentagem_acoes: float = Field(..., ge=0, le=100)
    porcentagem_fii: float = Field(..., ge=0, le=100)
    
    @model_validator(mode='after')
    def validate_porcentagens(self):
        if abs((self.porcentagem_acoes + self.porcentagem_fii) - 100.0) > 0.01:
            raise ValueError("A soma das porcentagens deve ser 100%")
        return self


class ConfiguracaoCreate(ConfiguracaoBase):
    pass


class ConfiguracaoUpdate(BaseModel):
    porcentagem_acoes: Optional[float] = Field(None, ge=0, le=100)
    porcentagem_fii: Optional[float] = Field(None, ge=0, le=100)


class ConfiguracaoResponse(ConfiguracaoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Schemas de Carteira
class CarteiraBase(BaseModel):
    valor_total: float = Field(default=0.0, ge=0)


class CarteiraResponse(CarteiraBase):
    id: int
    user_id: int
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class CarteiraResumo(BaseModel):
    valor_total: float
    valor_acoes: float
    valor_fiis: float
    porcentagem_acoes: float
    porcentagem_fiis: float
    total_ativos: int
    total_acoes: int
    total_fiis: int


# Schemas de Investimento
class SugestaoInvestimento(BaseModel):
    ativo_id: int
    codigo: str
    nome: str
    tipo: str
    quantidade_adicionar: int
    valor_investir: float
    quantidade_atual: int
    quantidade_sugerida: int
    preco_unitario: float


class FitnessDetalhado(BaseModel):
    uso_aporte: float
    aloc_geral: float
    aloc_especifica: float


class HistoricoFitnessItem(BaseModel):
    geracao: int
    fitness: float
    fitness_detalhado: FitnessDetalhado


class ResultadoInvestimento(BaseModel):
    sugestoes: List[SugestaoInvestimento]
    valor_total_atual: float
    valor_total_projetado: float
    valor_aporte: float
    valor_restante: float
    fitness: float
    algoritmo: str
    historico_fitness: Optional[List[HistoricoFitnessItem]] = None


