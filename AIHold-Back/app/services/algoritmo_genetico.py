import random
from typing import List, Dict, Tuple
from app.schemas import AtivoResponse


class Individuo:
    """Representa um indivíduo no algoritmo genético"""
    def __init__(self, carteira: List[Dict], valor_aporte: float, criar_vazio: bool = False):
        self.genes: List[int] = []
        self.fitness: float = 0.0
        self.fitness_detalhado: Dict = {}
        
        if not criar_vazio:
            self.gerar_genes_com_orcamento(carteira, valor_aporte)
    
    def gerar_genes_com_orcamento(self, carteira: List[Dict], valor_aporte: float):
        """Gera genes (quantidades) respeitando o orçamento"""
        orcamento_restante = valor_aporte
        incrementos = [0] * len(carteira)
        indices_aleatorios = list(range(len(carteira)))
        random.shuffle(indices_aleatorios)
        
        for i in indices_aleatorios:
            ativo = carteira[i]
            if orcamento_restante < ativo["preco"]:
                continue
            
            max_pode_comprar = int(orcamento_restante / ativo["preco"])
            quantidade_a_comprar = random.randint(0, max_pode_comprar)
            
            if quantidade_a_comprar > 0:
                incrementos[i] = quantidade_a_comprar
                orcamento_restante -= quantidade_a_comprar * ativo["preco"]
        
        self.genes = [
            carteira[i]["quantidade"] + incrementos[i] 
            for i in range(len(carteira))
        ]


class AlgoritmoGeneticoService:
    """Serviço para algoritmo genético de otimização de carteira"""
    
    def __init__(self):
        self.max_geracoes = 50
        self.taxa_mutacao = 0.1
        self.chance_mutacao_por_gene = 0.05
        self.taxa_crossover = 0.8
        self.numero_de_elites = 2
        self.multiplicador_tamanho_populacao = 20
    
    def validar_e_configurar_investimento(self, config: Dict) -> Dict:
        """Valida e normaliza as porcentagens"""
        config_corrigida = config.copy()
        
        for tipo in ['acao', 'fii']:
            if tipo in config_corrigida.get('alocacao_individual', {}):
                alocacoes = config_corrigida['alocacao_individual'][tipo]
                soma = sum(alocacoes.values())
                if abs(soma - 100.0) > 0.01:
                    for ticker in alocacoes:
                        alocacoes[ticker] = (alocacoes[ticker] / soma) * 100
        
        return config_corrigida
    
    def criar_populacao_inicial(self, tamanho: int, carteira: List[Dict], valor_aporte: float) -> List[Individuo]:
        """Cria população inicial"""
        return [Individuo(carteira, valor_aporte) for _ in range(tamanho)]
    
    def selecao_por_roleta_de_ranking(self, populacao_ordenada: List[Individuo]) -> Individuo:
        """Seleção por roleta baseada em ranking"""
        N = len(populacao_ordenada)
        soma_dos_ranks = (N * (N + 1)) / 2
        ponteiro_roleta = random.random() * soma_dos_ranks
        soma_acumulada = 0
        
        for i in range(N):
            rank = N - i
            soma_acumulada += rank
            if ponteiro_roleta <= soma_acumulada:
                return populacao_ordenada[i]
        
        return populacao_ordenada[N - 1]
    
    def crossover_de_um_ponto(self, pai1: Individuo, pai2: Individuo) -> Tuple[Individuo, Individuo]:
        """Crossover de um ponto"""
        filho1 = Individuo(None, None, criar_vazio=True)
        filho2 = Individuo(None, None, criar_vazio=True)
        
        num_genes = len(pai1.genes)
        ponto_de_corte = random.randint(1, num_genes - 1)
        
        filho1.genes = pai1.genes[:ponto_de_corte] + pai2.genes[ponto_de_corte:]
        filho2.genes = pai2.genes[:ponto_de_corte] + pai1.genes[ponto_de_corte:]
        
        return filho1, filho2
    
    def funcao_de_reparo(self, individuo: Individuo, carteira: List[Dict], valor_aporte: float):
        """Repara indivíduo para respeitar orçamento"""
        def calcular_custo(genes):
            return sum(
                (genes[i] - carteira[i]["quantidade"]) * carteira[i]["preco"]
                for i in range(len(genes))
                if genes[i] > carteira[i]["quantidade"]
            )
        
        custo_atual = calcular_custo(individuo.genes)
        
        while custo_atual > valor_aporte:
            indices_comprados = [
                i for i in range(len(individuo.genes))
                if individuo.genes[i] > carteira[i]["quantidade"]
            ]
            
            if not indices_comprados:
                break
            
            indice_aleatorio = random.choice(indices_comprados)
            individuo.genes[indice_aleatorio] -= 1
            custo_atual -= carteira[indice_aleatorio]["preco"]
    
    def mutacao_por_ajuste_fino(self, individuo: Individuo, chance_por_gene: float, 
                               carteira: List[Dict], valor_aporte: float):
        """Mutação por ajuste fino"""
        custo_original = sum(
            (individuo.genes[i] - carteira[i]["quantidade"]) * carteira[i]["preco"]
            for i in range(len(individuo.genes))
            if individuo.genes[i] > carteira[i]["quantidade"]
        )
        
        incrementos_originais = [
            individuo.genes[i] - carteira[i]["quantidade"]
            for i in range(len(individuo.genes))
        ]
        
        for i in range(len(individuo.genes)):
            if random.random() < chance_por_gene:
                ativo = carteira[i]
                mudanca = random.randint(-5, 5)
                incremento_antigo = incrementos_originais[i]
                novo_incremento = max(0, incremento_antigo + mudanca)
                
                custo_da_mudanca = (novo_incremento - incremento_antigo) * ativo["preco"]
                
                if custo_original + custo_da_mudanca <= valor_aporte:
                    individuo.genes[i] = carteira[i]["quantidade"] + novo_incremento
                    custo_original += custo_da_mudanca
    
    def calcular_fitness_uso_aporte(self, individuo: Individuo, carteira: List[Dict], valor_aporte: float) -> float:
        """Calcula fitness baseado no uso do aporte"""
        custo_aporte_realizado = sum(
            (individuo.genes[i] - carteira[i]["quantidade"]) * carteira[i]["preco"]
            for i in range(len(individuo.genes))
            if individuo.genes[i] > carteira[i]["quantidade"]
        )
        
        if custo_aporte_realizado > valor_aporte:
            return 0.0
        if valor_aporte == 0:
            return 1.0
        
        return custo_aporte_realizado / valor_aporte
    
    def calcular_fitness_alocacao_geral(self, carteira_final: List[Dict], settings: Dict) -> float:
        """Calcula fitness baseado na alocação geral (ações vs FIIs)"""
        valor_total_final = sum(ativo["valor_total"] for ativo in carteira_final)
        if valor_total_final == 0:
            return 0.0
        
        valores_reais_classe = {}
        for ativo in carteira_final:
            tipo = ativo["tipo"]
            if tipo not in valores_reais_classe:
                valores_reais_classe[tipo] = 0
            valores_reais_classe[tipo] += ativo["valor_total"]
        
        erro_total = 0.0
        alocacao_classe = settings.get("alocacao_classe", {})
        
        for tipo in alocacao_classe:
            valor_real = valores_reais_classe.get(tipo, 0)
            porcentagem_real = (valor_real / valor_total_final) * 100
            porcentagem_ideal = alocacao_classe[tipo]
            erro_total += abs(porcentagem_real - porcentagem_ideal)
        
        return 1 - (erro_total / 200)
    
    def calcular_fitness_alocacao_especifica(self, carteira_final: List[Dict], settings: Dict) -> float:
        """Calcula fitness baseado na alocação específica de cada ativo"""
        valores_totais_classe = {}
        for ativo in carteira_final:
            tipo = ativo["tipo"]
            if tipo not in valores_totais_classe:
                valores_totais_classe[tipo] = 0
            valores_totais_classe[tipo] += ativo["valor_total"]
        
        erro_normalizado_total = 0.0
        alocacao_individual = settings.get("alocacao_individual", {})
        numero_classes = len(alocacao_individual)
        
        for tipo in alocacao_individual:
            erro_classe = 0.0
            valor_total_classe = valores_totais_classe.get(tipo, 0)
            
            if valor_total_classe > 0:
                for ativo in carteira_final:
                    if ativo["tipo"] == tipo:
                        porcentagem_real = (ativo["valor_total"] / valor_total_classe) * 100
                        porcentagem_ideal = alocacao_individual[tipo].get(ativo["codigo"], 0)
                        if porcentagem_ideal is not None:
                            erro_classe += abs(porcentagem_real - porcentagem_ideal)
            
            erro_normalizado_total += erro_classe / 200
        
        return 1 - (erro_normalizado_total / numero_classes) if numero_classes > 0 else 0.0
    
    def calcular_fitness_ponderado(self, individuo: Individuo, carteira: List[Dict], settings: Dict) -> float:
        """Calcula fitness ponderado"""
        valor_aporte = settings["valor_aporte"]
        
        carteira_final_simulada = [
            {
                **carteira[i],
                "quantidade": individuo.genes[i],
                "valor_total": individuo.genes[i] * carteira[i]["preco"]
            }
            for i in range(len(carteira))
        ]
        
        fitness_uso = self.calcular_fitness_uso_aporte(individuo, carteira, valor_aporte)
        fitness_aloc_geral = self.calcular_fitness_alocacao_geral(carteira_final_simulada, settings)
        fitness_aloc_especifica = self.calcular_fitness_alocacao_especifica(carteira_final_simulada, settings)
        
        individuo.fitness_detalhado = {
            "uso_aporte": fitness_uso,
            "aloc_geral": fitness_aloc_geral,
            "aloc_especifica": fitness_aloc_especifica
        }
        
        pesos = {"uso": 0.2, "geral": 0.4, "especifica": 0.4}
        return (fitness_uso * pesos["uso"]) + (fitness_aloc_geral * pesos["geral"]) + (fitness_aloc_especifica * pesos["especifica"])
    
    def avaliar_populacao(self, populacao: List[Individuo], carteira: List[Dict], settings: Dict):
        """Avalia todos os indivíduos da população"""
        for individuo in populacao:
            individuo.fitness = self.calcular_fitness_ponderado(individuo, carteira, settings)
    
    def crossover_estrategico(self, pai1: Individuo, pai2: Individuo, carteira: List[Dict], settings: Dict) -> Tuple[Individuo, Individuo]:
        """Crossover estratégico com reparo e seleção elitista"""
        filho1, filho2 = self.crossover_de_um_ponto(pai1, pai2)
        
        self.funcao_de_reparo(filho1, carteira, settings["valor_aporte"])
        self.funcao_de_reparo(filho2, carteira, settings["valor_aporte"])
        
        filho1.fitness = self.calcular_fitness_ponderado(filho1, carteira, settings)
        filho2.fitness = self.calcular_fitness_ponderado(filho2, carteira, settings)
        
        familia = [pai1, pai2, filho1, filho2]
        familia.sort(key=lambda x: x.fitness, reverse=True)
        
        return familia[0], familia[1]
    
    def gerar_sugestoes(self, ativos: List[AtivoResponse], configuracoes: Dict, valor_aporte: float) -> Dict:
        """Gera sugestões de investimento usando algoritmo genético"""
        carteira = [
            {
                "codigo": ativo.codigo,
                "tipo": ativo.tipo,
                "quantidade": ativo.quantidade,
                "preco": ativo.preco
            }
            for ativo in ativos
        ]
        
        alocacao_classe = {
            "acao": configuracoes["porcentagem_acoes"],
            "fii": configuracoes["porcentagem_fii"]
        }
        
        alocacao_individual = {}
        acoes = [a for a in ativos if a.tipo == "acao"]
        fiis = [a for a in ativos if a.tipo == "fii"]
        
        alocacao_individual["acao"] = {ativo.codigo: ativo.porcentagem_ideal for ativo in acoes}
        alocacao_individual["fii"] = {ativo.codigo: ativo.porcentagem_ideal for ativo in fiis}
        
        config_investimento = {
            "valor_aporte": valor_aporte,
            "alocacao_classe": alocacao_classe,
            "alocacao_individual": alocacao_individual
        }
        
        config_investimento_validada = self.validar_e_configurar_investimento(config_investimento)
        
        tamanho_populacao = len(carteira) * self.multiplicador_tamanho_populacao
        
        populacao = self.criar_populacao_inicial(tamanho_populacao, carteira, valor_aporte)
        self.avaliar_populacao(populacao, carteira, config_investimento_validada)
        
        melhor_solucao_geral = max(populacao, key=lambda x: x.fitness)
        
        historico_fitness = []
        melhor_inicial = max(populacao, key=lambda x: x.fitness)
        historico_fitness.append({
            "geracao": 0,
            "fitness": melhor_inicial.fitness,
            "fitness_detalhado": melhor_inicial.fitness_detalhado.copy()
        })
        
        for geracao in range(1, self.max_geracoes + 1):
            populacao.sort(key=lambda x: x.fitness, reverse=True)
            
            nova_populacao = populacao[:self.numero_de_elites].copy()
            
            while len(nova_populacao) < tamanho_populacao:
                pai1 = self.selecao_por_roleta_de_ranking(populacao)
                pai2 = self.selecao_por_roleta_de_ranking(populacao)
                
                sobreviventes = self.crossover_estrategico(pai1, pai2, carteira, config_investimento_validada)
                
                for sobrevivente in sobreviventes:
                    if random.random() < self.taxa_mutacao:
                        self.mutacao_por_ajuste_fino(
                            sobrevivente, 
                            self.chance_mutacao_por_gene, 
                            carteira, 
                            valor_aporte
                        )
                        sobrevivente.fitness = self.calcular_fitness_ponderado(sobrevivente, carteira, config_investimento_validada)
                    
                    if len(nova_populacao) < tamanho_populacao:
                        nova_populacao.append(sobrevivente)
            
            populacao = nova_populacao
            self.avaliar_populacao(populacao, carteira, config_investimento_validada)
            
            melhor_da_geracao = max(populacao, key=lambda x: x.fitness)
            
            historico_fitness.append({
                "geracao": geracao,
                "fitness": melhor_da_geracao.fitness,
                "fitness_detalhado": melhor_da_geracao.fitness_detalhado.copy()
            })
            
            if melhor_da_geracao.fitness > melhor_solucao_geral.fitness:
                melhor_solucao_geral = melhor_da_geracao
        
        sugestoes = []
        custo_total_aporte = 0.0
        
        for i in range(len(melhor_solucao_geral.genes)):
            ativo = ativos[i]
            qtd_comprar = melhor_solucao_geral.genes[i] - ativo.quantidade
            
            if qtd_comprar > 0:
                custo = qtd_comprar * ativo.preco
                custo_total_aporte += custo
                
                sugestoes.append({
                    "ativo": ativo,
                    "quantidade_atual": ativo.quantidade,
                    "quantidade_sugerida": melhor_solucao_geral.genes[i],
                    "quantidade_adicionar": qtd_comprar,
                    "valor_investir": custo,
                    "tipo": ativo.tipo
                })
        
        valor_total_atual = sum(ativo.preco * ativo.quantidade for ativo in ativos)
        valor_total_projetado = sum(
            melhor_solucao_geral.genes[i] * carteira[i]["preco"]
            for i in range(len(carteira))
        )
        
        return {
            "sugestoes": sugestoes,
            "valor_total_atual": valor_total_atual,
            "valor_total_projetado": valor_total_projetado,
            "fitness": melhor_solucao_geral.fitness,
            "fitness_detalhado": melhor_solucao_geral.fitness_detalhado,
            "custo_total_aporte": custo_total_aporte,
            "melhor_cromossomo": melhor_solucao_geral.genes,
            "historico_fitness": historico_fitness
        }


algoritmo_genetico_service = AlgoritmoGeneticoService()



