import api from './api';

/**
 * Serviço de API para substituir o database.js
 * Mantém a mesma interface para compatibilidade
 */

export const ativosService = {
  /**
   * Adiciona ou atualiza um ativo
   */
  async adicionarAtivo(ativo) {
    try {
      const payload = {
        codigo: (ativo.codigo || '').trim().toUpperCase(),
        quantidade: parseInt(ativo.quantidade || 0),
        porcentagem_ideal: parseFloat(ativo.porcentagemIdeal || ativo.porcentagem_ideal || 0),
      };

      if (ativo.nome) {
        payload.nome = ativo.nome.trim();
      }
      if (ativo.tipo) {
        payload.tipo = ativo.tipo;
      }
      if (ativo.preco !== undefined && ativo.preco !== null && ativo.preco !== '') {
        payload.preco = parseFloat(ativo.preco);
      }

      console.log('Payload enviado ao backend:', payload);

      const data = await api.post('/api/ativos/', payload);
      
      console.log('Resposta do backend:', data);
      return data;
    } catch (error) {
      console.error('Erro ao adicionar ativo:', error);
      if (error.data && error.data.detail) {
        throw new Error(error.data.detail);
      }
      throw error;
    }
  },

  /**
   * Obtém todos os ativos
   */
  async obterTodosAtivos() {
    try {
      const data = await api.get('/api/ativos/');
      return data.map(ativo => ({
        id: ativo.id,
        codigo: ativo.codigo,
        nome: ativo.nome,
        tipo: ativo.tipo,
        preco: ativo.preco,
        quantidade: ativo.quantidade,
        porcentagemIdeal: ativo.porcentagem_ideal,
      }));
    } catch (error) {
      console.error('Erro ao obter ativos:', error);
      throw error;
    }
  },

  /**
   * Atualiza os preços de todos os ativos buscando na API brapi.dev
   */
  async atualizarPrecosAtivos() {
    try {
      console.log('Atualizando preços dos ativos...');
      const data = await api.post('/api/ativos/atualizar-precos');
      console.log('Preços atualizados com sucesso');
      return data.map(ativo => ({
        id: ativo.id,
        codigo: ativo.codigo,
        nome: ativo.nome,
        tipo: ativo.tipo,
        preco: ativo.preco,
        quantidade: ativo.quantidade,
        porcentagemIdeal: ativo.porcentagem_ideal,
      }));
    } catch (error) {
      console.error('Erro ao atualizar preços dos ativos:', error);
      throw error;
    }
  },

  /**
   * Zera a quantidade de todos os ativos da carteira
   */
  async zerarQuantidadesAtivos() {
    try {
      console.log('Zerando quantidades dos ativos...');
      const data = await api.post('/api/ativos/zerar-quantidades');
      console.log('Quantidades zeradas com sucesso');
      return data.map(ativo => ({
        id: ativo.id,
        codigo: ativo.codigo,
        nome: ativo.nome,
        tipo: ativo.tipo,
        preco: ativo.preco,
        quantidade: ativo.quantidade,
        porcentagemIdeal: ativo.porcentagem_ideal,
      }));
    } catch (error) {
      console.error('Erro ao zerar quantidades dos ativos:', error);
      throw error;
    }
  },

  /**
   * Obtém ativos por tipo
   */
  async obterAtivosPorTipo(tipo) {
    try {
      const data = await api.get(`/api/ativos/?tipo=${tipo}`);
      return data.map(ativo => ({
        id: ativo.id,
        codigo: ativo.codigo,
        nome: ativo.nome,
        tipo: ativo.tipo,
        preco: ativo.preco,
        quantidade: ativo.quantidade,
        porcentagemIdeal: ativo.porcentagem_ideal,
      }));
    } catch (error) {
      console.error('Erro ao obter ativos por tipo:', error);
      throw error;
    }
  },

  /**
   * Atualiza um ativo
   */
  async atualizarAtivo(id, dados) {
    try {
      const updateData = {};
      
      if (dados.codigo !== undefined) updateData.codigo = dados.codigo;
      if (dados.nome !== undefined) updateData.nome = dados.nome;
      if (dados.tipo !== undefined) updateData.tipo = dados.tipo;
      if (dados.preco !== undefined) updateData.preco = dados.preco;
      if (dados.quantidade !== undefined) updateData.quantidade = dados.quantidade;
      if (dados.porcentagemIdeal !== undefined) updateData.porcentagem_ideal = dados.porcentagemIdeal;
      
      const data = await api.put(`/api/ativos/${id}`, updateData);
      return data;
    } catch (error) {
      console.error('Erro ao atualizar ativo:', error);
      throw error;
    }
  },

  /**
   * Remove um ativo
   */
  async removerAtivo(id) {
    try {
      await api.delete(`/api/ativos/${id}`);
      return true;
    } catch (error) {
      console.error('Erro ao remover ativo:', error);
      throw error;
    }
  },

  /**
   * Busca ativo por código
   */
  async buscarAtivoPorCodigo(codigo) {
    try {
      const data = await api.get(`/api/ativos/buscar/codigo/${codigo}`);
      return {
        id: data.id,
        codigo: data.codigo,
        nome: data.nome,
        tipo: data.tipo,
        preco: data.preco,
        quantidade: data.quantidade,
        porcentagemIdeal: data.porcentagem_ideal,
      };
    } catch (error) {
      if (error.message.includes('404')) {
        return null;
      }
      console.error('Erro ao buscar ativo por código:', error);
      throw error;
    }
  },

};

export const configuracoesService = {
  /**
   * Salva configurações
   */
  async salvarConfiguracoes(config) {
    try {
      const data = await api.put('/api/configuracoes/', {
        porcentagem_acoes: config.porcentagemAcoes,
        porcentagem_fii: config.porcentagemFii,
      });
      
      return {
        porcentagemAcoes: data.porcentagem_acoes,
        porcentagemFii: data.porcentagem_fii,
      };
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
      throw error;
    }
  },

  /**
   * Obtém configurações
   */
  async obterConfiguracoes() {
    try {
      const data = await api.get('/api/configuracoes/');
      return {
        porcentagemAcoes: data.porcentagem_acoes,
        porcentagemFii: data.porcentagem_fii,
      };
    } catch (error) {
      console.error('Erro ao obter configurações:', error);
      return { porcentagemAcoes: 50, porcentagemFii: 50 };
    }
  },
};

export const carteiraService = {
  /**
   * Salva carteira (mantido para compatibilidade)
   */
  async salvarCarteira(dados) {
    try {
      // No backend, a carteira é calculada automaticamente
      // Apenas garantir que o resumo está atualizado
      await this.obterCarteira();
      return true;
    } catch (error) {
      console.error('Erro ao salvar carteira:', error);
      throw error;
    }
  },

  /**
   * Obtém informações da carteira
   */
  async obterCarteira() {
    try {
      const data = await api.get('/api/carteira/');
      return {
        valorTotal: data.valor_total,
        dataAtualizacao: data.data_atualizacao,
      };
    } catch (error) {
      console.error('Erro ao obter carteira:', error);
      throw error;
    }
  },

  /**
   * Calcula valor total da carteira
   */
  async calcularValorTotal() {
    try {
      const data = await api.get('/api/carteira/valor-total');
      return data.valor_total || 0;
    } catch (error) {
      console.error('Erro ao calcular valor total:', error);
      try {
        const ativos = await ativosService.obterTodosAtivos();
        return ativos.reduce((total, ativo) => {
          return total + (ativo.preco * ativo.quantidade);
        }, 0);
      } catch (e) {
        return 0;
      }
    }
  },
};

export const inicializarDadosDemo = async () => {
  console.log('Inicializando dados de demonstração...');
  
  try {
    const ativosExistentes = await ativosService.obterTodosAtivos();
    console.log('Ativos existentes:', ativosExistentes.length);
    
    if (ativosExistentes.length === 0) {
      console.log('Nenhum ativo encontrado. Inicializando dados de demonstração...');
      const dadosIniciais = [
        { codigo: "VALE3", nome: "Vale", tipo: 'acao', quantidade: 0, preco: 68.20, porcentagemIdeal: 16 },
        { codigo: "ITUB4", nome: "Itaú Unibanco", tipo: 'acao', quantidade: 0, preco: 32.15, porcentagemIdeal: 16 },
        { codigo: "IAJI11", nome: "IAJI11", tipo: 'acao', quantidade: 0, preco: 46.60, porcentagemIdeal: 17 },
        { codigo: "RETES", nome: "RETES", tipo: 'acao', quantidade: 0, preco: 66.60, porcentagemIdeal: 17 },
        { codigo: "ABEV3", nome: "Ambev", tipo: 'acao', quantidade: 0, preco: 14.72, porcentagemIdeal: 17 },
        { codigo: "B3SA3", nome: "B3", tipo: 'acao', quantidade: 0, preco: 12.91, porcentagemIdeal: 17 },
        { codigo: "BTAL11", nome: "BTAL11", tipo: 'fii', quantidade: 0, preco: 98.70, porcentagemIdeal: 16 },
        { codigo: "BTLG11", nome: "BTLG11", tipo: 'fii', quantidade: 0, preco: 120.45, porcentagemIdeal: 16 },
        { codigo: "CPTS11", nome: "CPTS11", tipo: 'fii', quantidade: 0, preco: 104.30, porcentagemIdeal: 17 },
        { codigo: "DEVA11", nome: "DEVA11", tipo: 'fii', quantidade: 0, preco: 112.50, porcentagemIdeal: 17 },
        { codigo: "FIIB11", nome: "FIIB11", tipo: 'fii', quantidade: 0, preco: 276.90, porcentagemIdeal: 17 },
        { codigo: "GTWR11", nome: "GTWR11", tipo: 'fii', quantidade: 0, preco: 87.60, porcentagemIdeal: 17 },
      ];

      for (const ativo of dadosIniciais) {
        await ativosService.adicionarAtivo(ativo);
      }
      console.log(`${dadosIniciais.length} ativos adicionados ao banco de dados`);

      await configuracoesService.salvarConfiguracoes({
        porcentagemAcoes: 50,
        porcentagemFii: 50
      });
      console.log('Configurações salvas');

      const valorTotal = await carteiraService.calcularValorTotal();
      await carteiraService.salvarCarteira({ valorTotal });
      console.log('Carteira salva com valor total:', valorTotal);
    } else {
      console.log('Dados já existem no banco de dados');
    }
    console.log('Inicialização de dados concluída');
  } catch (error) {
    console.error('Erro ao inicializar dados:', error);
  }
};

