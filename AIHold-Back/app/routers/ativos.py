from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Ativo
from app.schemas import AtivoCreate, AtivoUpdate, AtivoResponse
from app.auth import get_current_active_user
from app.services.brapi_service import BrapiService

router = APIRouter()

# Instância lazy do serviço brapi (criada apenas quando necessário)
_brapi_service = None

def get_brapi_service() -> BrapiService:
    """Retorna uma instância do serviço brapi (singleton)"""
    global _brapi_service
    if _brapi_service is None:
        _brapi_service = BrapiService()
    return _brapi_service


@router.get("/", response_model=List[AtivoResponse])
async def listar_ativos(
    tipo: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista todos os ativos do usuário"""
    query = db.query(Ativo).filter(Ativo.user_id == current_user.id)
    
    if tipo:
        if tipo not in ["acao", "fii"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo deve ser 'acao' ou 'fii'"
            )
        query = query.filter(Ativo.tipo == tipo)
    
    return query.all()


@router.get("/{ativo_id}", response_model=AtivoResponse)
async def obter_ativo(
    ativo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém um ativo específico"""
    ativo = db.query(Ativo).filter(
        Ativo.id == ativo_id,
        Ativo.user_id == current_user.id
    ).first()
    
    if not ativo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo não encontrado"
        )
    
    return ativo


@router.post("/", response_model=AtivoResponse, status_code=status.HTTP_201_CREATED)
async def criar_ativo(
    ativo_data: AtivoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo ativo.
    Se nome, tipo ou preco não forem fornecidos, busca automaticamente na API brapi.dev
    """
    codigo_normalizado = ativo_data.codigo.upper()
    
    # Verificar se já existe ativo com mesmo código para o usuário
    ativo_existente = db.query(Ativo).filter(
        Ativo.codigo == codigo_normalizado,
        Ativo.user_id == current_user.id
    ).first()
    
    # Preparar dados do ativo
    ativo_dict = ativo_data.dict(exclude_unset=True)
    ativo_dict['codigo'] = codigo_normalizado
    
    # Se nome, tipo ou preco não foram fornecidos, buscar na API brapi
    precisa_buscar = not ativo_dict.get('nome') or not ativo_dict.get('tipo') or not ativo_dict.get('preco')
    
    if precisa_buscar:
        try:
            brapi_service = get_brapi_service()
            info_brapi = brapi_service.buscar_informacoes_ativo(codigo_normalizado)
            
            if not info_brapi:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ativo {codigo_normalizado} não encontrado na API brapi.dev. Verifique se o código está correto e se é uma ação ou FII válido."
                )
            
            # Preencher campos faltantes com dados da API
            if not ativo_dict.get('nome'):
                ativo_dict['nome'] = info_brapi.get('nome')
            if not ativo_dict.get('tipo'):
                ativo_dict['tipo'] = info_brapi.get('tipo')
            if not ativo_dict.get('preco'):
                ativo_dict['preco'] = info_brapi.get('preco')
                
            print(f"[AtivosRouter] Dados buscados da API: {info_brapi}")
            
        except HTTPException:
            # Re-raise HTTPExceptions (como 404)
            raise
        except Exception as e:
            # Outros erros da API
            print(f"[AtivosRouter] Erro ao buscar informações na API brapi: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar informações do ativo {codigo_normalizado} na API brapi.dev: {str(e)}"
            )
    
    # Validar que todos os campos obrigatórios estão presentes
    if not ativo_dict.get('nome') or not ativo_dict.get('tipo') or not ativo_dict.get('preco'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível obter todas as informações necessárias do ativo. Por favor, forneça nome, tipo e preco manualmente."
        )
    
    if ativo_existente:
        # Atualizar ativo existente
        for key, value in ativo_dict.items():
            if key != 'codigo':  # Não atualizar código
                setattr(ativo_existente, key, value)
        db.commit()
        db.refresh(ativo_existente)
        return ativo_existente
    
    # Criar novo ativo
    db_ativo = Ativo(**ativo_dict, user_id=current_user.id)
    db.add(db_ativo)
    db.commit()
    db.refresh(db_ativo)
    return db_ativo


@router.put("/{ativo_id}", response_model=AtivoResponse)
async def atualizar_ativo(
    ativo_id: int,
    ativo_data: AtivoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza um ativo"""
    ativo = db.query(Ativo).filter(
        Ativo.id == ativo_id,
        Ativo.user_id == current_user.id
    ).first()
    
    if not ativo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo não encontrado"
        )
    
    update_data = ativo_data.dict(exclude_unset=True)
    if "codigo" in update_data:
        update_data["codigo"] = update_data["codigo"].upper()
    
    for key, value in update_data.items():
        setattr(ativo, key, value)
    
    db.commit()
    db.refresh(ativo)
    return ativo


@router.delete("/{ativo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_ativo(
    ativo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deleta um ativo"""
    ativo = db.query(Ativo).filter(
        Ativo.id == ativo_id,
        Ativo.user_id == current_user.id
    ).first()
    
    if not ativo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo não encontrado"
        )
    
    db.delete(ativo)
    db.commit()
    return None


@router.get("/buscar/codigo/{codigo}", response_model=AtivoResponse)
async def buscar_ativo_por_codigo(
    codigo: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Busca um ativo pelo código"""
    ativo = db.query(Ativo).filter(
        Ativo.codigo == codigo.upper(),
        Ativo.user_id == current_user.id
    ).first()
    
    if not ativo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo não encontrado"
        )
    
    return ativo


@router.post("/atualizar-precos", response_model=List[AtivoResponse])
async def atualizar_precos_ativos(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza os preços de todos os ativos do usuário buscando na API brapi.dev
    """
    try:
        brapi_service = get_brapi_service()
        ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
        
        if not ativos:
            return []
        
        ativos_atualizados = []
        ativos_com_erro = []
        
        for ativo in ativos:
            try:
                # Buscar informações atualizadas na API
                info_brapi = brapi_service.buscar_informacoes_ativo(ativo.codigo)
                
                if info_brapi:
                    # Atualizar preço
                    ativo.preco = info_brapi.get('preco', ativo.preco)
                    # Atualizar nome se mudou
                    if info_brapi.get('nome'):
                        ativo.nome = info_brapi.get('nome')
                    # Atualizar tipo se mudou (improvável, mas por segurança)
                    if info_brapi.get('tipo'):
                        ativo.tipo = info_brapi.get('tipo')
                    
                    ativos_atualizados.append(ativo)
                else:
                    ativos_com_erro.append(ativo.codigo)
                    print(f"[AtivosRouter] Não foi possível atualizar {ativo.codigo}")
                    
            except Exception as e:
                print(f"[AtivosRouter] Erro ao atualizar {ativo.codigo}: {str(e)}")
                ativos_com_erro.append(ativo.codigo)
        
        db.commit()
        
        # Refresh dos objetos atualizados
        for ativo in ativos_atualizados:
            db.refresh(ativo)
        
        if ativos_com_erro:
            print(f"[AtivosRouter] Ativos com erro na atualização: {ativos_com_erro}")
        
        return ativos_atualizados
        
    except Exception as e:
        db.rollback()
        print(f"[AtivosRouter] Erro ao atualizar preços: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar preços dos ativos: {str(e)}"
        )


@router.post("/zerar-quantidades", response_model=List[AtivoResponse])
async def zerar_quantidades_ativos(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Zera a quantidade de todos os ativos da carteira do usuário
    """
    try:
        ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
        
        if not ativos:
            return []
        
        for ativo in ativos:
            ativo.quantidade = 0
        
        db.commit()
        
        # Refresh dos objetos atualizados
        for ativo in ativos:
            db.refresh(ativo)
        
        return ativos
        
    except Exception as e:
        db.rollback()
        print(f"[AtivosRouter] Erro ao zerar quantidades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao zerar quantidades dos ativos: {str(e)}"
        )


