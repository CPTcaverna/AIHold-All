from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Ativo, Carteira
from app.schemas import CarteiraResumo, CarteiraResponse
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/resumo", response_model=CarteiraResumo)
async def obter_resumo_carteira(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calcula e retorna resumo da carteira"""
    ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
    
    valor_total = sum(ativo.preco * ativo.quantidade for ativo in ativos)
    valor_acoes = sum(
        ativo.preco * ativo.quantidade 
        for ativo in ativos 
        if ativo.tipo == "acao"
    )
    valor_fiis = sum(
        ativo.preco * ativo.quantidade 
        for ativo in ativos 
        if ativo.tipo == "fii"
    )
    
    porcentagem_acoes = (valor_acoes / valor_total * 100) if valor_total > 0 else 0
    porcentagem_fiis = (valor_fiis / valor_total * 100) if valor_total > 0 else 0
    
    total_acoes = len([ativo for ativo in ativos if ativo.tipo == "acao"])
    total_fiis = len([ativo for ativo in ativos if ativo.tipo == "fii"])
    
    # Atualizar registro da carteira
    carteira = db.query(Carteira).filter(Carteira.user_id == current_user.id).first()
    if carteira:
        carteira.valor_total = valor_total
    else:
        carteira = Carteira(user_id=current_user.id, valor_total=valor_total)
        db.add(carteira)
    db.commit()
    
    return CarteiraResumo(
        valor_total=valor_total,
        valor_acoes=valor_acoes,
        valor_fiis=valor_fiis,
        porcentagem_acoes=porcentagem_acoes,
        porcentagem_fiis=porcentagem_fiis,
        total_ativos=len(ativos),
        total_acoes=total_acoes,
        total_fiis=total_fiis
    )


@router.get("/valor-total", response_model=dict)
async def calcular_valor_total(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calcula o valor total da carteira"""
    ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
    valor_total = sum(ativo.preco * ativo.quantidade for ativo in ativos)
    
    return {"valor_total": valor_total}


@router.get("/", response_model=CarteiraResponse)
async def obter_carteira(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém informações da carteira"""
    carteira = db.query(Carteira).filter(Carteira.user_id == current_user.id).first()
    
    if not carteira:
        # Calcular valor total
        ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
        valor_total = sum(ativo.preco * ativo.quantidade for ativo in ativos)
        
        # Criar carteira
        carteira = Carteira(user_id=current_user.id, valor_total=valor_total)
        db.add(carteira)
        db.commit()
        db.refresh(carteira)
    
    return carteira



