from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Ativo
from app.schemas import ResultadoInvestimento, SugestaoInvestimento
from app.auth import get_current_active_user
from app.services.algoritmo_genetico import algoritmo_genetico_service
from app.services.algoritmo_deterministico import deterministic_optimizer_service

router = APIRouter()


def validar_porcentagens_ideais(ativos: List[Ativo]) -> None:
    """
    Valida se a soma das porcentagens ideais dos ativos é exatamente 100% para cada tipo
    (ações e FIIs devem somar 100% cada um individualmente)
    
    Raises:
        HTTPException: Se a soma não for exatamente 100% para algum tipo
    """
    # Separar ativos por tipo
    acoes = [ativo for ativo in ativos if ativo.tipo == 'acao']
    fiis = [ativo for ativo in ativos if ativo.tipo == 'fii']
    
    erros = []
    
    # Validar ações
    if acoes:
        soma_acoes = sum(ativo.porcentagem_ideal for ativo in acoes)
        if abs(soma_acoes - 100.0) > 0.01:
            erros.append(
                f"Ações: soma atual é {soma_acoes:.2f}% (deve ser 100%)"
            )
    
    # Validar FIIs
    if fiis:
        soma_fiis = sum(ativo.porcentagem_ideal for ativo in fiis)
        if abs(soma_fiis - 100.0) > 0.01:
            erros.append(
                f"FIIs: soma atual é {soma_fiis:.2f}% (deve ser 100%)"
            )
    
    # Se houver erros, lançar exceção
    if erros:
        mensagem_erro = (
            "A soma das porcentagens ideais deve ser exatamente 100% para cada tipo (ações e FIIs).\n\n"
            + "\n".join(erros)
            + "\n\nPor favor, ajuste as porcentagens ideais dos seus ativos na página de configuração."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem_erro
        )


@router.get("/sugestoes", response_model=ResultadoInvestimento)
async def gerar_sugestoes_investimento(
    valor_aporte: float = Query(..., gt=0, description="Valor disponível para investir"),
    algoritmo: str = Query(default="genetico", pattern="^(genetico|deterministico)$", description="Algoritmo a usar"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Gera sugestões de investimento usando algoritmo genético ou determinístico"""
    # Buscar ativos e configurações
    ativos = db.query(Ativo).filter(Ativo.user_id == current_user.id).all()
    
    if not ativos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum ativo encontrado na carteira"
        )
    
    # Validar se as porcentagens ideais somam 100%
    validar_porcentagens_ideais(ativos)
    
    # Buscar configurações
    from app.models import Configuracao
    config = db.query(Configuracao).filter(Configuracao.user_id == current_user.id).first()
    
    if not config:
        configuracoes = {"porcentagem_acoes": 50.0, "porcentagem_fii": 50.0}
    else:
        configuracoes = {
            "porcentagem_acoes": config.porcentagem_acoes,
            "porcentagem_fii": config.porcentagem_fii
        }
    
    # Gerar sugestões
    if algoritmo == "genetico":
        resultado = algoritmo_genetico_service.gerar_sugestoes(ativos, configuracoes, valor_aporte)
    else:
        resultado = deterministic_optimizer_service.gerar_sugestoes(ativos, configuracoes, valor_aporte)
    
    # Converter para formato de resposta
    sugestoes_formatadas = []
    valor_total_investido = 0.0
    
    for sugestao in resultado["sugestoes"]:
        ativo = sugestao["ativo"]
        sugestoes_formatadas.append(
            SugestaoInvestimento(
                ativo_id=ativo.id,
                codigo=ativo.codigo,
                nome=ativo.nome,
                tipo=ativo.tipo,
                quantidade_adicionar=sugestao["quantidade_adicionar"],
                valor_investir=sugestao["valor_investir"],
                quantidade_atual=ativo.quantidade,
                quantidade_sugerida=sugestao.get("quantidade_sugerida", ativo.quantidade + sugestao["quantidade_adicionar"]),
                preco_unitario=ativo.preco
            )
        )
        valor_total_investido += sugestao["valor_investir"]
    
    valor_restante = valor_aporte - valor_total_investido
    
    # Converter histórico de fitness se existir
    historico_fitness = None
    if "historico_fitness" in resultado and resultado["historico_fitness"]:
        from app.schemas import HistoricoFitnessItem, FitnessDetalhado
        historico_fitness = [
            HistoricoFitnessItem(
                geracao=item["geracao"],
                fitness=item["fitness"],
                fitness_detalhado=FitnessDetalhado(**item["fitness_detalhado"])
            )
            for item in resultado["historico_fitness"]
        ]
    
    return ResultadoInvestimento(
        sugestoes=sugestoes_formatadas,
        valor_total_atual=resultado["valor_total_atual"],
        valor_total_projetado=resultado["valor_total_projetado"],
        valor_aporte=valor_aporte,
        valor_restante=valor_restante,
        fitness=resultado.get("fitness", 0.0),
        algoritmo=algoritmo,
        historico_fitness=historico_fitness
    )

