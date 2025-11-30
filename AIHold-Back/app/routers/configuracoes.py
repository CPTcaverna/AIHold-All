from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Configuracao
from app.schemas import ConfiguracaoCreate, ConfiguracaoUpdate, ConfiguracaoResponse
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=ConfiguracaoResponse)
async def obter_configuracoes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém as configurações do usuário"""
    config = db.query(Configuracao).filter(
        Configuracao.user_id == current_user.id
    ).first()
    
    if not config:
        # Criar configuração padrão se não existir
        config = Configuracao(
            user_id=current_user.id,
            porcentagem_acoes=50.0,
            porcentagem_fii=50.0
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config


@router.put("/", response_model=ConfiguracaoResponse)
async def atualizar_configuracoes(
    config_data: ConfiguracaoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza as configurações do usuário"""
    config = db.query(Configuracao).filter(
        Configuracao.user_id == current_user.id
    ).first()
    
    if not config:
        # Criar configuração se não existir
        porcentagem_acoes = config_data.porcentagem_acoes or 50.0
        porcentagem_fii = config_data.porcentagem_fii or 50.0
        
        # Ajustar se a soma não for 100
        if abs((porcentagem_acoes + porcentagem_fii) - 100.0) > 0.01:
            porcentagem_fii = 100.0 - porcentagem_acoes
        
        config = Configuracao(
            user_id=current_user.id,
            porcentagem_acoes=porcentagem_acoes,
            porcentagem_fii=porcentagem_fii
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config
    
    # Atualizar configuração existente
    update_data = config_data.dict(exclude_unset=True)
    
    # Se uma porcentagem foi fornecida, ajustar a outra
    if "porcentagem_acoes" in update_data and "porcentagem_fii" not in update_data:
        update_data["porcentagem_fii"] = 100.0 - update_data["porcentagem_acoes"]
    elif "porcentagem_fii" in update_data and "porcentagem_acoes" not in update_data:
        update_data["porcentagem_acoes"] = 100.0 - update_data["porcentagem_fii"]
    
    # Validar soma
    porcentagem_acoes = update_data.get("porcentagem_acoes", config.porcentagem_acoes)
    porcentagem_fii = update_data.get("porcentagem_fii", config.porcentagem_fii)
    
    if abs((porcentagem_acoes + porcentagem_fii) - 100.0) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A soma das porcentagens deve ser 100%"
        )
    
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.post("/", response_model=ConfiguracaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_configuracoes(
    config_data: ConfiguracaoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cria configurações para o usuário"""
    # Verificar se já existe
    existing = db.query(Configuracao).filter(
        Configuracao.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configurações já existem. Use PUT para atualizar."
        )
    
    # Validar soma
    if abs((config_data.porcentagem_acoes + config_data.porcentagem_fii) - 100.0) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A soma das porcentagens deve ser 100%"
        )
    
    config = Configuracao(
        user_id=current_user.id,
        **config_data.dict()
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config



