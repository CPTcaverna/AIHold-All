from typing import List, Dict
from app.schemas import AtivoResponse


class DeterministicOptimizerService:
    """Serviço para algoritmo determinístico de otimização de carteira"""
    
    def calcular_total_valor(self, assets: List[Dict]) -> float:
        """Calcula valor total dos ativos"""
        return sum(asset["price"] * asset["quantity"] for asset in assets)
    
    def calcular_valores_categoria(self, assets: List[Dict]) -> Dict[str, float]:
        """Calcula valores por categoria"""
        stocks_value = sum(
            asset["price"] * asset["quantity"]
            for asset in assets
            if asset["type"] == "stock"
        )
        reits_value = sum(
            asset["price"] * asset["quantity"]
            for asset in assets
            if asset["type"] == "reit"
        )
        return {"stocks_value": stocks_value, "reits_value": reits_value}
    
    def calcular_max_unidades(self, available_value: float, price: float) -> int:
        """Calcula máximo de unidades que podem ser compradas"""
        return int(available_value / price) if price > 0 else 0
    
    def calcular_distribuicao_atual(self, assets: List[Dict]) -> Dict[str, float]:
        """Calcula distribuição atual do portfólio"""
        total_value = self.calcular_total_valor(assets)
        if total_value == 0:
            return {"stocks": 0.0, "reits": 0.0}
        
        stocks_value = sum(
            asset["price"] * asset["quantity"]
            for asset in assets
            if asset["type"] == "stock"
        )
        reits_value = sum(
            asset["price"] * asset["quantity"]
            for asset in assets
            if asset["type"] == "reit"
        )
        
        return {
            "stocks": (stocks_value / total_value) * 100,
            "reits": (reits_value / total_value) * 100
        }
    
    def gerar_sugestao_basica(self, current_assets: List[Dict], settings: Dict, available_value: float) -> Dict:
        """Gera sugestão inteligente comprando 1 unidade por vez do ativo com menor porcentagem ideal"""
        stocks_percentage = settings.get("stocks_percentage", 50)
        reits_percentage = settings.get("reits_percentage", 50)
        
        total_current_value = self.calcular_total_valor(current_assets)
        new_total_value = total_current_value + available_value
        
        ideal_stocks_value = new_total_value * (stocks_percentage / 100)
        ideal_reits_value = new_total_value * (reits_percentage / 100)
        
        stocks_assets = [a for a in current_assets if a["type"] == "stock"]
        reits_assets = [a for a in current_assets if a["type"] == "reit"]
        
        for asset in stocks_assets:
            porcentagem_ideal = asset.get("porcentagem_ideal", 0)
            if porcentagem_ideal == 0 and stocks_assets:
                porcentagem_ideal = 100 / len(stocks_assets)
            asset["ideal_value"] = ideal_stocks_value * (porcentagem_ideal / 100)
        
        for asset in reits_assets:
            porcentagem_ideal = asset.get("porcentagem_ideal", 0)
            if porcentagem_ideal == 0 and reits_assets:
                porcentagem_ideal = 100 / len(reits_assets)
            asset["ideal_value"] = ideal_reits_value * (porcentagem_ideal / 100)
        
        quantidades_compra = {asset["ticker"]: 0 for asset in current_assets}
        suggestions = []
        remaining_value = available_value
        
        while remaining_value > 0:
            melhor_asset = None
            maior_deficit = -1
            
            for asset in current_assets:
                current_value = asset["price"] * (asset["quantity"] + quantidades_compra[asset["ticker"]])
                ideal_value = asset.get("ideal_value", 0)
                
                if ideal_value > 0:
                    deficit = max(0, ideal_value - current_value)
                    deficit_percentual = (deficit / ideal_value) * 100
                else:
                    deficit_percentual = 0
                
                if asset["price"] <= remaining_value and deficit_percentual > maior_deficit:
                    maior_deficit = deficit_percentual
                    melhor_asset = asset
            
            if melhor_asset:
                ticker = melhor_asset["ticker"]
                quantidades_compra[ticker] += 1
                remaining_value -= melhor_asset["price"]
            else:
                break
        
        for asset in current_assets:
            qtd_comprar = quantidades_compra[asset["ticker"]]
            if qtd_comprar > 0:
                investment_value = qtd_comprar * asset["price"]
                current_value = asset["price"] * asset["quantity"]
                ideal_value = asset.get("ideal_value", 0)
                
                deficit_percentual = 0
                if ideal_value > 0:
                    deficit = max(0, ideal_value - current_value)
                    deficit_percentual = (deficit / ideal_value) * 100
                
                suggestions.append({
                    "ticker": asset["ticker"],
                    "name": asset["name"],
                    "type": asset["type"],
                    "price": asset["price"],
                    "quantity_to_buy": qtd_comprar,
                    "value": investment_value,
                    "deficit_percentage": deficit_percentual
                })
        
        quantidades = {ticker: qtd for ticker, qtd in quantidades_compra.items() if qtd > 0}
        fitness = sum(s["value"] for s in suggestions)
        
        return {
            "quantidades": quantidades,
            "fitness": fitness,
            "sugestoes": suggestions
        }
    
    def gerar_sugestoes(self, ativos: List[AtivoResponse], configuracoes: Dict, valor_aporte: float) -> Dict:
        """Gera sugestões de investimento usando algoritmo determinístico"""
        ativos_formatados = [
            {
                "ticker": ativo.codigo,
                "name": ativo.nome,
                "type": "stock" if ativo.tipo == "acao" else "reit",
                "price": ativo.preco,
                "quantity": ativo.quantidade,
                "porcentagem_ideal": ativo.porcentagem_ideal
            }
            for ativo in ativos
        ]
        
        settings = {
            "stocks_percentage": configuracoes.get("porcentagem_acoes", 50),
            "reits_percentage": configuracoes.get("porcentagem_fii", 50)
        }
        
        resultado = self.gerar_sugestao_basica(ativos_formatados, settings, valor_aporte)
        
        sugestoes = []
        valor_total_investido = 0.0
        
        if resultado.get("sugestoes") and isinstance(resultado["sugestoes"], list):
            for sugestao in resultado["sugestoes"]:
                ativo = next((a for a in ativos if a.codigo == sugestao["ticker"]), None)
                if ativo and sugestao["quantity_to_buy"] > 0:
                    valor_investir = sugestao["quantity_to_buy"] * ativo.preco
                    valor_total_investido += valor_investir
                    
                    sugestoes.append({
                        "ativo": ativo,
                        "quantidade_adicionar": sugestao["quantity_to_buy"],
                        "valor_investir": valor_investir
                    })
        
        valor_total_atual = sum(ativo.preco * ativo.quantidade for ativo in ativos)
        valor_total_projetado = valor_total_atual + valor_total_investido
        
        return {
            "sugestoes": sugestoes,
            "fitness": resultado.get("fitness", 0),
            "melhor_solucao": {
                "genes": list(resultado.get("quantidades", {}).values()),
                "fitness": resultado.get("fitness", 0)
            },
            "valor_total_atual": valor_total_atual,
            "valor_total_projetado": valor_total_projetado
        }


deterministic_optimizer_service = DeterministicOptimizerService()



