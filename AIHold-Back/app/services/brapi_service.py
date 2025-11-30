"""
Serviço para integração com a API brapi.dev
Busca informações de ativos (ações e FIIs) automaticamente
"""
from typing import Optional, Dict
from brapi import Brapi
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class BrapiService:
    """Serviço para buscar informações de ativos na API brapi.dev"""
    
    def __init__(self):
        # Obter token da API - a SDK brapi exige uma API key
        api_key = os.getenv("BRAPI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "BRAPI_API_KEY não configurada. Defina a chave no arquivo .env."
            )
        self.api_key = api_key
        self.client = Brapi(api_key=api_key)
        self.base_url = "https://brapi.dev/api"
    
    def buscar_informacoes_ativo(self, codigo: str) -> Optional[Dict]:
        """
        Busca informações de um ativo na API brapi.dev
        
        Args:
            codigo: Código do ativo (ex: PETR4, HGLG11)
            
        Returns:
            Dict com informações do ativo ou None se não encontrado
            {
                'nome': str,
                'tipo': 'acao' ou 'fii',
                'preco': float
            }
        """
        try:
            # Buscar cotação do ativo
            codigo_upper = codigo.upper()
            print(f"[BrapiService] Buscando ativo: {codigo_upper}")
            
            quote = self.client.quote.retrieve(tickers=codigo_upper)
            
            if not quote.results or len(quote.results) == 0:
                print(f"[BrapiService] Nenhum resultado encontrado para {codigo_upper}")
                return None
            
            resultado = quote.results[0]
            
            # Verificar todos os atributos disponíveis para debug
            atributos_disponiveis = [attr for attr in dir(resultado) if not attr.startswith('_')]
            print(f"[BrapiService] Atributos disponíveis: {atributos_disponiveis}")
            
            # Tentar acessar o campo 'type' diretamente da API de múltiplas formas
            # A API brapi retorna "type": "stock" ou "type": "fund"
            tipo_api = None
            
            # Tentar diferentes formas de acessar o campo type
            if hasattr(resultado, 'type'):
                tipo_api = resultado.type
                print(f"[BrapiService] Campo 'type' encontrado via atributo: {tipo_api}")
            elif hasattr(resultado, 'quote_type'):
                tipo_api = resultado.quote_type
                print(f"[BrapiService] Campo 'quote_type' encontrado: {tipo_api}")
            elif hasattr(resultado, '__dict__'):
                # Tentar acessar via __dict__ se disponível
                resultado_dict = resultado.__dict__
                if 'type' in resultado_dict:
                    tipo_api = resultado_dict['type']
                    print(f"[BrapiService] Campo 'type' encontrado via __dict__: {tipo_api}")
                elif 'quote_type' in resultado_dict:
                    tipo_api = resultado_dict['quote_type']
                    print(f"[BrapiService] Campo 'quote_type' encontrado via __dict__: {tipo_api}")
            
            # Se ainda não encontrou, tentar acessar via getattr com diferentes nomes
            if not tipo_api:
                for attr_name in ['type', 'quote_type', 'asset_type', 'stock_type']:
                    try:
                        valor = getattr(resultado, attr_name, None)
                        if valor:
                            tipo_api = valor
                            print(f"[BrapiService] Campo '{attr_name}' encontrado: {tipo_api}")
                            break
                    except:
                        pass
            
            # Se ainda não encontrou o tipo, fazer uma requisição HTTP direta para obter o campo 'type'
            if not tipo_api:
                print(f"[BrapiService] Campo 'type' não encontrado na SDK, fazendo requisição HTTP direta...")
                try:
                    url = f"{self.base_url}/quote/list"
                    params = {
                        'search': codigo_upper,
                        'limit': 1,
                        'token': self.api_key
                    }
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        # A API retorna stocks e indexes, verificar ambos
                        if 'stocks' in data and len(data['stocks']) > 0:
                            stock_data = data['stocks'][0]
                            if 'type' in stock_data:
                                tipo_api = stock_data['type']
                                print(f"[BrapiService] Tipo encontrado via API HTTP direta: {tipo_api}")
                except Exception as e:
                    print(f"[BrapiService] Erro ao buscar tipo via HTTP direta: {str(e)}")
            
            print(f"[BrapiService] Resultado recebido: symbol={resultado.symbol}, type={tipo_api}, long_name={getattr(resultado, 'long_name', None)}, short_name={getattr(resultado, 'short_name', None)}")
            
            # Extrair informações
            nome = resultado.long_name or resultado.short_name or codigo_upper
            preco = resultado.regular_market_price
            
            print(f"[BrapiService] Nome extraído: {nome}, Preço: {preco}")
            
            if preco is None or preco <= 0:
                print(f"[BrapiService] Preço inválido para {codigo_upper}: {preco}")
                return None
            
            # Determinar tipo do ativo usando o campo 'type' da API
            # A API retorna "stock" para ações e "fund" para FIIs
            tipo = self._determinar_tipo(codigo_upper, resultado, tipo_api)
            print(f"[BrapiService] Tipo detectado: {tipo}")
            
            return {
                'nome': nome,
                'tipo': tipo,
                'preco': float(preco)
            }
            
        except Exception as e:
            # Log do erro detalhado
            import traceback
            print(f"[BrapiService] Erro ao buscar ativo {codigo}: {str(e)}")
            print(f"[BrapiService] Traceback: {traceback.format_exc()}")
            return None
    
    def _determinar_tipo(self, codigo: str, resultado, tipo_api: Optional[str] = None) -> str:
        """
        Determina se o ativo é ação ou FII
        
        Args:
            codigo: Código do ativo
            resultado: Resultado da API brapi
            tipo_api: Tipo retornado diretamente pela API ("stock" ou "fund")
            
        Returns:
            'acao' ou 'fii'
        """
        print(f"[BrapiService] Determinando tipo para código: {codigo}, tipo_api: {tipo_api}")
        
        # 1. PRIORIDADE: Usar o campo 'type' diretamente da API
        # A API brapi retorna "type": "stock" para ações e "type": "fund" para FIIs
        if tipo_api:
            tipo_lower = str(tipo_api).lower()
            print(f"[BrapiService] Tipo da API encontrado: {tipo_lower}")
            if tipo_lower == 'fund':
                print(f"[BrapiService] Identificado como FII pelo campo 'type' da API")
                return 'fii'
            elif tipo_lower == 'stock':
                print(f"[BrapiService] Identificado como ação pelo campo 'type' da API")
                return 'acao'
        
        # 2. Verificar se o código termina em 11 (padrão comum para FIIs)
        # FIIs no Brasil geralmente terminam em 11 (ex: HGLG11, VISC11, MXRF11)
        if codigo.endswith('11'):
            print(f"[BrapiService] Código termina em 11, identificado como FII")
            return 'fii'
        
        # 3. Verificar no nome do ativo se contém palavras-chave de FII
        nome_ativo = (resultado.long_name or resultado.short_name or "").upper()
        palavras_fii = [
            'FUNDO', 
            'FII', 
            'FUNDO IMOBILIÁRIO', 
            'FUNDO DE INVESTIMENTO IMOBILIÁRIO',
            'FUNDO DE INVESTIMENTO',
            'REAL ESTATE',
            'FIIF',
            'FII-',
            'FII '
        ]
        
        for palavra in palavras_fii:
            if palavra in nome_ativo:
                print(f"[BrapiService] Palavra-chave '{palavra}' encontrada no nome, identificado como FII")
                return 'fii'
        
        # 4. Verificar atributos do resultado da API como fallback
        # Verificar se há informação de quoteType no resultado (se disponível)
        if hasattr(resultado, 'quote_type') and resultado.quote_type:
            quote_type = str(resultado.quote_type).lower()
            print(f"[BrapiService] quote_type encontrado: {quote_type}")
            if quote_type == 'fund' or 'fund' in quote_type:
                return 'fii'
            elif quote_type == 'stock' or 'stock' in quote_type:
                return 'acao'
        
        # Verificar se há informação de assetType no resultado (se disponível)
        if hasattr(resultado, 'asset_type') and resultado.asset_type:
            asset_type = str(resultado.asset_type).lower()
            print(f"[BrapiService] asset_type encontrado: {asset_type}")
            if asset_type == 'fund' or 'fund' in asset_type:
                return 'fii'
            elif asset_type == 'stock' or 'stock' in asset_type:
                return 'acao'
        
        # Verificar se há informação de sector ou industry (FIIs geralmente têm sector relacionado a imóveis)
        if hasattr(resultado, 'sector') and resultado.sector:
            sector = str(resultado.sector).upper()
            print(f"[BrapiService] sector encontrado: {sector}")
            if 'REAL ESTATE' in sector or 'IMOBILIÁRIO' in sector or 'FII' in sector:
                return 'fii'
        
        # 5. Se não encontrou indicação de FII, assumimos que é ação
        print(f"[BrapiService] Nenhuma indicação de FII encontrada, identificado como ação")
        return 'acao'

