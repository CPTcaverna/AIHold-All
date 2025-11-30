import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import { ativosService, configuracoesService } from '../../services/apiService';
import api from '../../services/api';
import './Investir.css';

const Investir = () => {
  const navigate = useNavigate();
  const [ativos, setAtivos] = useState([]);
  const [configuracoes, setConfiguracoes] = useState({ porcentagemAcoes: 50, porcentagemFii: 50 });
  const [valorAporte, setValorAporte] = useState(500);
  const algoritmoEscolhido = 'genetico';
  const [sugestoes, setSugestoes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aplicandoTodas, setAplicandoTodas] = useState(false);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      const [ativosData, configData] = await Promise.all([
        ativosService.obterTodosAtivos(),
        configuracoesService.obterConfiguracoes()
      ]);
      
      setAtivos(ativosData);
      setConfiguracoes(configData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const calcularSugestoes = async () => {
    // Verificar se há ativos antes de tentar gerar sugestões
    if (!ativos || ativos.length === 0) {
      alert(
        '⚠️ Nenhum ativo encontrado na carteira!\n\n' +
        'Para receber sugestões de investimento, você precisa adicionar ativos à sua carteira primeiro.\n\n' +
        'Vá até a página "Minha Carteira" e adicione seus ativos (ações e FIIs) antes de tentar investir.'
      );
      return;
    }

    // Validar se as porcentagens ideais somam 100% para cada tipo (ações e FIIs)
    const acoes = ativos.filter(ativo => ativo.tipo === 'acao');
    const fiis = ativos.filter(ativo => ativo.tipo === 'fii');
    
    const erros = [];
    
    if (acoes.length > 0) {
      const somaAcoes = acoes.reduce((soma, ativo) => soma + (ativo.porcentagemIdeal || 0), 0);
      if (Math.abs(somaAcoes - 100) > 0.01) {
        erros.push(`Ações: soma atual é ${somaAcoes.toFixed(2)}% (deve ser 100%)`);
      }
    }
    
    if (fiis.length > 0) {
      const somaFiis = fiis.reduce((soma, ativo) => soma + (ativo.porcentagemIdeal || 0), 0);
      if (Math.abs(somaFiis - 100) > 0.01) {
        erros.push(`FIIs: soma atual é ${somaFiis.toFixed(2)}% (deve ser 100%)`);
      }
    }
    
    if (erros.length > 0) {
      alert(
        `❌ Erro: Porcentagens Ideais Invalidas\n\n` +
        `A soma das porcentagens ideais deve ser exatamente 100% para cada tipo (ações e FIIs).\n\n` +
        erros.join('\n') +
        `\n\nPor favor, ajuste as porcentagens ideais dos seus ativos na página de Configuração antes de investir.`
      );
      return;
    }

    setLoading(true);
    
    try {
      // Atualizar preços dos ativos antes de calcular sugestões
      console.log('Atualizando preços dos ativos antes de calcular sugestões...');
      try {
        await ativosService.atualizarPrecosAtivos();
        // Recarregar ativos com preços atualizados
        await carregarDados();
        console.log('Preços atualizados com sucesso');
      } catch (error) {
        console.error('Erro ao atualizar preços antes de calcular sugestões:', error);
        // Continuar mesmo se a atualização falhar
      }
      
      // Usar o endpoint do backend com query parameters
      const url = `/api/investimentos/sugestoes?valor_aporte=${valorAporte}&algoritmo=${algoritmoEscolhido}`;
      const resultado = await api.get(url);
      
      // Converter formato do backend para formato esperado pelo frontend
      const sugestoesFormatadas = resultado.sugestoes.map(s => ({
        ativo: {
          id: s.ativo_id,
          codigo: s.codigo,
          nome: s.nome,
          tipo: s.tipo,
          preco: s.preco_unitario,
          quantidade: s.quantidade_atual,
        },
        quantidadeAdicionar: s.quantidade_adicionar,
        valorInvestir: s.valor_investir,
        tipo: s.tipo,
      }));
      
      setSugestoes({
        valorTotalAtual: resultado.valor_total_atual,
        valorTotalProjetado: resultado.valor_total_projetado,
        valorAporte: valorAporte,
        sugestoes: sugestoesFormatadas,
        valorRestante: resultado.valor_restante,
        fitness: resultado.fitness,
        algoritmo: algoritmoEscolhido
      });
    } catch (error) {
      console.error('Erro ao calcular sugestões:', error);
      
      // Verificar se o erro é sobre porcentagens ideais
      const errorMessage = error.message || '';
      const errorData = error.data || {};
      const errorDetail = errorData.detail || errorMessage;
      
      // Se o erro for sobre porcentagens ideais, mostrar mensagem específica
      if (errorDetail.includes('porcentagens ideais') || errorDetail.includes('100%')) {
        alert(`❌ ${errorDetail}`);
        setLoading(false);
        return;
      }
      const errorStatus = error.status || 0;
      
      if (errorStatus === 404 || (errorDetail && errorDetail.includes('Nenhum ativo encontrado'))) {
        alert(
          '⚠️ Nenhum ativo encontrado na carteira!\n\n' +
          'Para receber sugestões de investimento, você precisa adicionar ativos à sua carteira primeiro.\n\n' +
          'Vá até a página "Minha Carteira" e adicione seus ativos (ações e FIIs) antes de tentar investir.'
        );
      } else if (errorMessage.includes('conectar ao servidor') || errorMessage.includes('Failed to fetch') || errorMessage.includes('fetch')) {
        alert(
          '❌ Erro de Conexão\n\n' +
          'Não foi possível conectar ao backend.\n\n' +
          'Verifique:\n' +
          '1. Se o backend está rodando (uvicorn main:app --reload)\n' +
          '2. Se está na porta 8000 (http://localhost:8000)\n' +
          '3. Abra o console do navegador (F12) para mais detalhes'
        );
      } else {
        alert('Erro ao gerar sugestões: ' + (errorDetail || errorMessage || 'Erro desconhecido. Tente novamente.'));
      }
    } finally {
      setLoading(false);
    }
  };

  const aplicarSugestao = async (sugestao) => {
    try {
      const novaQuantidade = sugestao.ativo.quantidade + sugestao.quantidadeAdicionar;
      await ativosService.atualizarAtivo(sugestao.ativo.id, { quantidade: novaQuantidade });
      await carregarDados();
      alert(`Aplicada sugestão para ${sugestao.ativo.codigo}: +${sugestao.quantidadeAdicionar} unidades`);
    } catch (error) {
      console.error('Erro ao aplicar sugestão:', error);
      alert('Erro ao aplicar sugestão');
    }
  };

  const aplicarTodasSugestoes = async () => {
    if (!sugestoes || sugestoes.sugestoes.length === 0) {
      alert('Não há sugestões para aplicar');
      return;
    }

    const confirmacao = window.confirm(
      `Deseja aplicar todas as ${sugestoes.sugestoes.length} sugestões de investimento?\n\n` +
      `Total a ser investido: R$ ${sugestoes.sugestoes.reduce((sum, s) => sum + s.valorInvestir, 0).toFixed(2)}`
    );

    if (!confirmacao) return;

    setAplicandoTodas(true);
    
    try {
      const atualizacoes = [];
      
      // Preparar todas as atualizações
      for (const sugestao of sugestoes.sugestoes) {
        const novaQuantidade = sugestao.ativo.quantidade + sugestao.quantidadeAdicionar;
        atualizacoes.push(
          ativosService.atualizarAtivo(sugestao.ativo.id, { quantidade: novaQuantidade })
        );
      }

      // Aplicar todas as atualizações em paralelo
      await Promise.all(atualizacoes);
      
      // Recarregar dados e limpar sugestões
      await carregarDados();
      setSugestoes(null);
      
      alert(`✅ Todas as sugestões foram aplicadas com sucesso!\n\n` +
            `Total investido: R$ ${sugestoes.sugestoes.reduce((sum, s) => sum + s.valorInvestir, 0).toFixed(2)}\n` +
            `Ativos atualizados: ${sugestoes.sugestoes.length}`);
            
    } catch (error) {
      console.error('Erro ao aplicar todas as sugestões:', error);
      alert('Erro ao aplicar as sugestões. Tente novamente.');
    } finally {
      setAplicandoTodas(false);
    }
  };

  return (
    <div className="investir">
      <Navbar />
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Investir</h1>
            <p className="page-subtitle">Receba sugestões de investimento para otimizar sua carteira</p>
          </div>
        </div>

        {/* Aviso se não houver ativos */}
        {ativos.length === 0 && (
          <div className="card" style={{ backgroundColor: '#fff3cd', border: '1px solid #ffc107' }}>
            <h3 style={{ color: '#856404', marginTop: 0 }}>⚠️ Nenhum ativo encontrado</h3>
            <p style={{ color: '#856404' }}>
              Para receber sugestões de investimento, você precisa adicionar ativos à sua carteira primeiro.
            </p>
            <button 
              className="btn-primary" 
              onClick={() => navigate('/carteira')}
              style={{ marginTop: '10px' }}
            >
              Ir para Minha Carteira
            </button>
          </div>
        )}

        <div className="card">
          <div className="form-group">
            <label className="form-label">Algoritmo de Otimização</label>
            <div className="algoritmo-options">
              <div className="algoritmo-option">
                <input
                  type="radio"
                  name="algoritmo"
                  value="genetico"
                  defaultChecked
                  readOnly
                />
                <span className="algoritmo-label">
                  <span className="algoritmo-icon">🧬</span>
                  <div>
                    <div className="algoritmo-name">Algoritmo Genético</div>
                    <div className="algoritmo-desc">
                      Busca global com evolução de soluções. Este é o único algoritmo disponível no momento.
                    </div>
                  </div>
                </span>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Valor disponível para investir</label>
            <input
              type="number"
              className="form-input"
              placeholder="500"
              value={valorAporte}
              onChange={(e) => setValorAporte(parseFloat(e.target.value) || 0)}
              min="0"
              step="0.01"
            />
          </div>
          
          <button 
            className="btn-primary btn-gerar" 
            onClick={calcularSugestoes}
            disabled={loading || valorAporte <= 0 || ativos.length === 0}
          >
            {loading ? 'Gerando Sugestões...' : 'Gerar Sugestões (Algoritmo Genético)'}
          </button>
          {ativos.length === 0 && (
            <p style={{ color: '#856404', marginTop: '10px', fontSize: '0.9em' }}>
              Adicione ativos à sua carteira antes de gerar sugestões.
            </p>
          )}
        </div>

        {sugestoes && (
          <div className="card">
            <h2>Resultado das Sugestões (Algoritmo Genético)</h2>
            
            <div className="resumo-sugestoes">
              <div className="resumo-item">
                <span className="resumo-label">Valor Total Atual</span>
                <span className="resumo-valor">R$ {sugestoes.valorTotalAtual.toFixed(2)}</span>
              </div>
              <div className="resumo-item">
                <span className="resumo-label">Valor do Aporte</span>
                <span className="resumo-valor">R$ {sugestoes.valorAporte.toFixed(2)}</span>
              </div>
              <div className="resumo-item">
                <span className="resumo-label">Valor Total Projetado</span>
                <span className="resumo-valor">R$ {sugestoes.valorTotalProjetado.toFixed(2)}</span>
              </div>
            </div>

            {sugestoes.sugestoes.length > 0 ? (
              <>
                <div className="sugestoes-header">
                  <h3>Sugestões de Investimento</h3>
                  <button 
                    className="btn-success btn-aplicar-todas"
                    onClick={aplicarTodasSugestoes}
                    disabled={aplicandoTodas}
                  >
                    {aplicandoTodas ? 'Aplicando...' : '✅ Aplicar Todas'}
                  </button>
                </div>
                <div className="sugestoes-lista">
                  {sugestoes.sugestoes.map((sugestao, index) => (
                    <div key={index} className="sugestao-item">
                      <div className="sugestao-header">
                        <div className="sugestao-info">
                          <h4>{sugestao.ativo.codigo}</h4>
                          <p>{sugestao.ativo.nome}</p>
                          <span className="tipo-badge">{sugestao.tipo === 'acao' ? 'Ação' : 'FII'}</span>
                        </div>
                        <button 
                          className="btn-primary btn-aplicar"
                          onClick={() => aplicarSugestao(sugestao)}
                        >
                          Aplicar
                        </button>
                      </div>
                      
                      <div className="sugestao-detalhes">
                        <div className="detalhe-item">
                          <span>Quantidade atual:</span>
                          <span>{sugestao.ativo.quantidade}</span>
                        </div>
                        <div className="detalhe-item">
                          <span>Quantidade sugerida:</span>
                          <span>+{sugestao.quantidadeAdicionar}</span>
                        </div>
                        <div className="detalhe-item">
                          <span>Valor a investir:</span>
                          <span>R$ {sugestao.valorInvestir.toFixed(2)}</span>
                        </div>
                        <div className="detalhe-item">
                          <span>Preço unitário:</span>
                          <span>R$ {sugestao.ativo.preco.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {sugestoes.valorRestante > 0 && (
                  <div className="valor-restante">
                    <p>Valor restante não alocado: <strong>R$ {sugestoes.valorRestante.toFixed(2)}</strong></p>
                    <p className="texto-pequeno">Este valor pode ser mantido em caixa ou usado para outros investimentos.</p>
                  </div>
                )}
              </>
            ) : (
              <div className="sem-sugestoes">
                <p>Não foram encontradas sugestões de investimento com o valor disponível.</p>
                <p>Isso pode acontecer quando:</p>
                <ul>
                  <li>O valor do aporte é muito baixo para comprar pelo menos uma unidade dos ativos</li>
                  <li>Sua carteira já está bem alinhada com as configurações ideais</li>
                  <li>Não há ativos configurados com percentuais ideais</li>
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Investir;
