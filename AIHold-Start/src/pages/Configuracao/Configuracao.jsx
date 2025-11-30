import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import { ativosService, configuracoesService } from '../../services/apiService';
import './Configuracao.css';

const Configuracao = () => {
  const [ativos, setAtivos] = useState([]);
  const [configuracoes, setConfiguracoes] = useState({ porcentagemAcoes: 50, porcentagemFii: 50 });
  const [valorTotal, setValorTotal] = useState(0);
  const [loading, setLoading] = useState(false);

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
      
      const total = ativosData.reduce((sum, ativo) => sum + (ativo.preco * ativo.quantidade), 0);
      setValorTotal(total);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const handleDistribuicaoChange = (novoValor) => {
    setConfiguracoes({
      porcentagemAcoes: novoValor,
      porcentagemFii: 100 - novoValor
    });
  };

  const handlePorcentagemInternaChange = async (ativoId, novaPorcentagem) => {
    try {
      await ativosService.atualizarAtivo(ativoId, { porcentagemIdeal: novaPorcentagem });
      await carregarDados();
    } catch (error) {
      console.error('Erro ao atualizar porcentagem:', error);
    }
  };

  const handleSalvarConfiguracoes = async () => {
    setLoading(true);
    try {
      await configuracoesService.salvarConfiguracoes(configuracoes);
      alert('Configurações salvas com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
      alert('Erro ao salvar configurações');
    } finally {
      setLoading(false);
    }
  };

  const calcularPorcentagemCarteira = (porcentagemInterna, tipo) => {
    const porcentagemTipo = tipo === 'acao' ? configuracoes.porcentagemAcoes : configuracoes.porcentagemFii;
    return (porcentagemInterna / 100) * porcentagemTipo;
  };

  const calcularDiferenca = (ativo) => {
    const valorAtual = ativo.preco * ativo.quantidade;
    const porcentagemAtual = valorTotal > 0 ? (valorAtual / valorTotal) * 100 : 0;
    const porcentagemIdeal = calcularPorcentagemCarteira(ativo.porcentagemIdeal, ativo.tipo);
    return porcentagemAtual - porcentagemIdeal;
  };

  const calcularSomaExcessoFalta = (ativos) => {
    let totalExcesso = 0;
    let totalFalta = 0;
    
    ativos.forEach(ativo => {
      const diferenca = calcularDiferenca(ativo);
      if (diferenca > 0) {
        totalExcesso += diferenca;
      } else if (diferenca < 0) {
        totalFalta += Math.abs(diferenca);
      }
    });
    
    return { totalExcesso, totalFalta };
  };

  const obterCorDiferenca = (diferenca) => {
    if (Math.abs(diferenca) < 0.1) {
      return 'verde'; // Correto (0.0)
    } else if (diferenca > 0) {
      return 'azul'; // Excesso
    } else {
      return 'vermelho'; // Falta
    }
  };

  const acoes = ativos.filter(ativo => ativo.tipo === 'acao');
  const fiis = ativos.filter(ativo => ativo.tipo === 'fii');

  const totalInternoAcoes = acoes.reduce((sum, ativo) => sum + ativo.porcentagemIdeal, 0);
  const totalInternoFiis = fiis.reduce((sum, ativo) => sum + ativo.porcentagemIdeal, 0);

  const { totalExcesso: excessoAcoes, totalFalta: faltaAcoes } = calcularSomaExcessoFalta(acoes);
  const { totalExcesso: excessoFiis, totalFalta: faltaFiis } = calcularSomaExcessoFalta(fiis);

  return (
    <div className="configuracao">
      <Navbar />
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Configurações</h1>
            <p className="page-subtitle">Defina a alocação ideal da sua carteira</p>
          </div>
        </div>

        {/* Distribuição da Carteira */}
        <div className="card">
          <h2>Distribuição da Carteira</h2>
          <div className="distribuicao-slider">
            <div className="slider-container">
              <input
                type="range"
                min="0"
                max="100"
                value={configuracoes.porcentagemAcoes}
                onChange={(e) => handleDistribuicaoChange(parseInt(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>{configuracoes.porcentagemAcoes}% Ações</span>
                <span>{configuracoes.porcentagemFii}% FIIs</span>
              </div>
            </div>
            <div className="distribuicao-barra">
              <div className="distribuicao-item">
                <span>Ações</span>
                <div className="barra-progresso">
                  <div 
                    className="barra-fill acoes" 
                    style={{ width: `${configuracoes.porcentagemAcoes}%` }}
                  ></div>
                </div>
              </div>
              <div className="distribuicao-item">
                <span>FIIs</span>
                <div className="barra-progresso">
                  <div 
                    className="barra-fill fiis" 
                    style={{ width: `${configuracoes.porcentagemFii}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Alocação de Ações e FIIs lado a lado */}
        <div className="configuracao-tabelas">
          {/* Alocação de Ações */}
          <div className="card">
            <h2>Alocação de Ações ({configuracoes.porcentagemAcoes}%)</h2>
            <div className="totais-container">
              <p className="total-interno">Total interno: {totalInternoAcoes.toFixed(1)}%</p>
              <div className="somas-diferencas">
                <span className="soma-excesso">Excesso: {excessoAcoes.toFixed(1)}%</span>
                <span className="soma-falta">Falta: {faltaAcoes.toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="tabela-alocacao">
              <div className="tabela-header">
                <span>Ativo</span>
                <span>Atual</span>
                <span>% Interno</span>
                <span>% Carteira</span>
              </div>
              
              {acoes.map((ativo) => {
                const valorAtivo = ativo.preco * ativo.quantidade;
                const porcentagemAtual = valorTotal > 0 ? (valorAtivo / valorTotal) * 100 : 0;
                const porcentagemCarteira = calcularPorcentagemCarteira(ativo.porcentagemIdeal, ativo.tipo);
                const diferenca = calcularDiferenca(ativo);
                const corDiferenca = obterCorDiferenca(diferenca);
                
                return (
                  <div key={ativo.id} className="tabela-row">
                    <span className="ativo-codigo">{ativo.codigo}</span>
                    <span className="ativo-atual">{porcentagemAtual.toFixed(1)}%</span>
                    <div className="input-container">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={ativo.porcentagemIdeal}
                        onChange={(e) => handlePorcentagemInternaChange(ativo.id, parseFloat(e.target.value) || 0)}
                        className="input-porcentagem"
                      />
                      <span className={`diferenca ${corDiferenca}`}>
                        {diferenca > 0 ? '+' : ''}{diferenca.toFixed(1)}% ({diferenca > 0 ? 'excesso' : diferenca < 0 ? 'falta' : 'correto'})
                      </span>
                    </div>
                    <span className="ativo-carteira">{porcentagemCarteira.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Alocação de FIIs */}
          <div className="card">
            <h2>Alocação de FIIs ({configuracoes.porcentagemFii}%)</h2>
            <div className="totais-container">
              <p className="total-interno">Total interno: {totalInternoFiis.toFixed(1)}%</p>
              <div className="somas-diferencas">
                <span className="soma-excesso">Excesso: {excessoFiis.toFixed(1)}%</span>
                <span className="soma-falta">Falta: {faltaFiis.toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="tabela-alocacao">
              <div className="tabela-header">
                <span>Ativo</span>
                <span>Atual</span>
                <span>% Interno</span>
                <span>% Carteira</span>
              </div>
              
              {fiis.map((ativo) => {
                const valorAtivo = ativo.preco * ativo.quantidade;
                const porcentagemAtual = valorTotal > 0 ? (valorAtivo / valorTotal) * 100 : 0;
                const porcentagemCarteira = calcularPorcentagemCarteira(ativo.porcentagemIdeal, ativo.tipo);
                const diferenca = calcularDiferenca(ativo);
                const corDiferenca = obterCorDiferenca(diferenca);
                
                return (
                  <div key={ativo.id} className="tabela-row">
                    <span className="ativo-codigo">{ativo.codigo}</span>
                    <span className="ativo-atual">{porcentagemAtual.toFixed(1)}%</span>
                    <div className="input-container">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={ativo.porcentagemIdeal}
                        onChange={(e) => handlePorcentagemInternaChange(ativo.id, parseFloat(e.target.value) || 0)}
                        className="input-porcentagem"
                      />
                      <span className={`diferenca ${corDiferenca}`}>
                        {diferenca > 0 ? '+' : ''}{diferenca.toFixed(1)}% ({diferenca > 0 ? 'excesso' : diferenca < 0 ? 'falta' : 'correto'})
                      </span>
                    </div>
                    <span className="ativo-carteira">{porcentagemCarteira.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Informações */}
        <div className="card info-card">
          <h3>Informações sobre as configurações</h3>
          <ul>
            <li>A soma dos percentuais ideais para cada tipo de ativo (ações ou FIIs) não deve ultrapassar o valor máximo definido na distribuição da carteira.</li>
            <li>Por exemplo: Se na distribuição da carteira foi definido 50% para ações e 50% para FIIs, então, o somatório de todos os percentuais ideais para ações e FIIs não deve ultrapassar 50%.</li>
            <li>Quando há apenas um ativo de cada tipo, seu percentual é automaticamente definido como o valor do percentual definido para o tipo de ativo (ações ou FIIs).</li>
            <li>Por exemplo: Se na distribuição da carteira foi definido 50% para ações e 50% para FIIs, e se existe apenas uma ação na alocação, então, essa ação é configurada com percentual ideal de 50%.</li>
          </ul>
        </div>

        {/* Botão Salvar */}
        <div className="actions">
          <button 
            className="btn-primary" 
            onClick={handleSalvarConfiguracoes}
            disabled={loading}
          >
            {loading ? 'Salvando...' : 'Salvar Configurações'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Configuracao;
