import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import { ativosService, carteiraService } from '../../services/apiService';
import './Carteira.css';

const Carteira = () => {
  const [ativos, setAtivos] = useState([]);
  const [valorTotal, setValorTotal] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [novoAtivo, setNovoAtivo] = useState({ codigo: '', quantidade: '' });
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async (atualizarPrecos = false) => {
    try {
      setCarregando(true);
      
      // Se solicitado, atualizar preços antes de carregar
      if (atualizarPrecos) {
        try {
          await ativosService.atualizarPrecosAtivos();
        } catch (error) {
          console.error('Erro ao atualizar preços:', error);
          // Continuar mesmo se a atualização falhar
        }
      }
      
      const ativosData = await ativosService.obterTodosAtivos();
      const valorTotalData = await carteiraService.calcularValorTotal();
      
      setAtivos(ativosData);
      setValorTotal(valorTotalData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setCarregando(false);
    }
  };

  const calcularDistribuicao = () => {
    const acoes = ativos.filter(ativo => ativo.tipo === 'acao');
    const fiis = ativos.filter(ativo => ativo.tipo === 'fii');
    
    const valorAcoes = acoes.reduce((total, ativo) => total + (ativo.preco * ativo.quantidade), 0);
    const valorFiis = fiis.reduce((total, ativo) => total + (ativo.preco * ativo.quantidade), 0);
    
    const porcentagemAcoes = valorTotal > 0 ? (valorAcoes / valorTotal) * 100 : 0;
    const porcentagemFiis = valorTotal > 0 ? (valorFiis / valorTotal) * 100 : 0;
    
    return { porcentagemAcoes, porcentagemFiis };
  };

  const handleAdicionarAtivo = async () => {
    // Validações - apenas código é obrigatório
    if (!novoAtivo.codigo || !novoAtivo.codigo.trim()) {
      alert('Por favor, informe o código do ativo.');
      return;
    }

    const quantidade = novoAtivo.quantidade ? parseInt(novoAtivo.quantidade) : 0;

    if (novoAtivo.quantidade && (isNaN(quantidade) || quantidade < 0)) {
      alert('A quantidade deve ser um número maior ou igual a zero.');
      return;
    }

    try {
      setCarregando(true);
      // Enviar apenas o código - o backend buscará automaticamente nome, tipo e preço
      const ativoData = {
        codigo: novoAtivo.codigo.trim().toUpperCase(),
        quantidade: quantidade
      };
      
      console.log('Adicionando ativo:', ativoData);
      await ativosService.adicionarAtivo(ativoData);
      
      setNovoAtivo({ codigo: '', quantidade: '' });
      setShowModal(false);
      await carregarDados();
      
      alert('Ativo adicionado com sucesso! As informações foram buscadas automaticamente.');
    } catch (error) {
      console.error('Erro completo ao adicionar ativo:', error);
      const errorMessage = error.message || error.detail || 'Erro desconhecido ao adicionar ativo';
      
      // Mensagem mais amigável para erro de conexão
      if (errorMessage.includes('conectar ao servidor') || errorMessage.includes('Failed to fetch')) {
        alert(
          '❌ Erro de Conexão\n\n' +
          'Não foi possível conectar ao backend.\n\n' +
          'Verifique:\n' +
          '1. Se o backend está rodando (uvicorn main:app --reload)\n' +
          '2. Se está na porta 8000 (http://localhost:8000)\n' +
          '3. Abra o console do navegador (F12) para mais detalhes'
        );
      } else if (errorMessage.includes('não encontrado na API')) {
        alert('❌ Ativo não encontrado\n\n' + errorMessage + '\n\nVerifique se o código está correto.');
      } else {
        alert('Erro ao adicionar ativo: ' + errorMessage);
      }
    } finally {
      setCarregando(false);
    }
  };


  const handleAtualizarQuantidade = async (ativoId, novaQuantidade) => {
    if (novaQuantidade < 0) {
      alert('A quantidade não pode ser negativa!');
      return;
    }

    try {
      await ativosService.atualizarAtivo(ativoId, { quantidade: novaQuantidade });
      await carregarDados();
    } catch (error) {
      console.error('Erro ao atualizar quantidade:', error);
      alert('Erro ao atualizar quantidade: ' + error.message);
    }
  };

  const handleRemoverAtivo = async (ativoId) => {
    const confirmacao = window.confirm('Tem certeza que deseja remover este ativo? Esta ação não pode ser desfeita.');
    
    if (!confirmacao) return;

    try {
      await ativosService.removerAtivo(ativoId);
      await carregarDados();
      alert('Ativo removido com sucesso!');
    } catch (error) {
      console.error('Erro ao remover ativo:', error);
      alert('Erro ao remover ativo: ' + error.message);
    }
  };

  const handleZerarQuantidades = async () => {
    const confirmacao = window.confirm(
      'Tem certeza que deseja zerar a quantidade de todos os ativos na carteira?\n\n' +
      'Esta ação irá definir a quantidade de todos os ativos como 0. Esta ação não pode ser desfeita.'
    );
    
    if (!confirmacao) return;

    try {
      setCarregando(true);
      await ativosService.zerarQuantidadesAtivos();
      await carregarDados();
      alert('Quantidades zeradas com sucesso!');
    } catch (error) {
      console.error('Erro ao zerar quantidades:', error);
      alert('Erro ao zerar quantidades: ' + (error.message || error.detail || 'Erro desconhecido'));
    } finally {
      setCarregando(false);
    }
  };

  const handleEditarAtivo = (ativo) => {
    // Para editar, vamos apenas permitir editar a quantidade
    // O código, nome, tipo e preço são gerenciados pelo backend
    setNovoAtivo({
      codigo: ativo.codigo,
      quantidade: ativo.quantidade.toString()
    });
    setShowModal(true);
  };

  const distribuicao = calcularDistribuicao();
  const acoes = ativos.filter(ativo => ativo.tipo === 'acao');
  const fiis = ativos.filter(ativo => ativo.tipo === 'fii');

  return (
    <div className="carteira">
      <Navbar />
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Minha Carteira</h1>
            <p className="page-subtitle">Acompanhe seus investimentos</p>
          </div>
          <div className="header-actions">
            <button className="btn-secondary" onClick={() => carregarDados(true)} disabled={carregando}>
              {carregando ? 'Carregando...' : '🔄 Recarregar'}
            </button>
            <button className="btn-secondary" onClick={handleZerarQuantidades} disabled={carregando}>
              🗑️ Zerar Quantidades
            </button>
            <button className="btn-primary" onClick={() => setShowModal(true)}>
              + Adicionar Ativo
            </button>
          </div>
        </div>

        {/* Resumo da Carteira */}
        <div className="card">
          <h2>Resumo da Carteira</h2>
          {carregando ? (
            <div className="loading-indicator">
              <p>Carregando dados...</p>
            </div>
          ) : (
            <>
              <div className="resumo-grid">
                <div className="resumo-item">
                  <span className="resumo-label">Valor Total</span>
                  <span className="resumo-valor">R$ {valorTotal.toFixed(2)}</span>
                </div>
                <div className="resumo-item">
                  <span className="resumo-label">Ações</span>
                  <span className="resumo-valor">{distribuicao.porcentagemAcoes.toFixed(1)}%</span>
                </div>
                <div className="resumo-item">
                  <span className="resumo-label">FIIs</span>
                  <span className="resumo-valor">{distribuicao.porcentagemFiis.toFixed(1)}%</span>
                </div>
              </div>
          
              <div className="distribuicao-barra">
                <div className="distribuicao-item">
                  <span>Ações ({distribuicao.porcentagemAcoes.toFixed(1)}%)</span>
                  <div className="barra-progresso">
                    <div 
                      className="barra-fill acoes" 
                      style={{ width: `${distribuicao.porcentagemAcoes}%` }}
                    ></div>
                  </div>
                </div>
                <div className="distribuicao-item">
                  <span>FIIs ({distribuicao.porcentagemFiis.toFixed(1)}%)</span>
                  <div className="barra-progresso">
                    <div 
                      className="barra-fill fiis" 
                      style={{ width: `${distribuicao.porcentagemFiis}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Ações e FIIs lado a lado */}
        <div className="carteira-tabelas">
          {/* Ações */}
          <div className="card">
            <h2>Ações ({acoes.length})</h2>
            {carregando ? (
              <div className="loading-indicator">
                <p>Carregando ações...</p>
              </div>
            ) : acoes.length === 0 ? (
              <div className="empty-state">
                <p>Nenhuma ação encontrada. Adicione sua primeira ação!</p>
              </div>
            ) : (
              <div className="ativos-container">
                {acoes.map((ativo, index) => {
                  const valorAtivo = ativo.preco * ativo.quantidade;
                  const porcentagemCarteira = valorTotal > 0 ? (valorAtivo / valorTotal) * 100 : 0;
                  
                  return (
                    <div key={ativo.id || index} className="ativo-card acao">
                      <div className="ativo-header">
                        <div className="ativo-info">
                          <h3 className="ativo-codigo">{ativo.codigo}</h3>
                          <p className="ativo-nome">{ativo.nome}</p>
                        </div>
                        <button 
                          className="btn-delete-card"
                          onClick={() => handleRemoverAtivo(ativo.id)}
                          title="Remover ativo"
                        >
                          🗑️
                        </button>
                      </div>
                      
                      <div className="ativo-detalhes">
                        <div className="ativo-quantidade">
                          <span className="ativo-label">Quantidade</span>
                          <input
                            type="number"
                            value={ativo.quantidade}
                            onChange={(e) => handleAtualizarQuantidade(ativo.id, parseInt(e.target.value))}
                            className="quantidade-input"
                            min="0"
                          />
                        </div>
                        <div className="ativo-preco">
                          <span className="ativo-label">Preço</span>
                          <span className="ativo-valor">R$ {ativo.preco.toFixed(2)}</span>
                        </div>
                      </div>
                      
                      <div className="ativo-valor-total">
                        <span className="valor-total">R$ {valorAtivo.toFixed(2)}</span>
                        <span className="porcentagem">({porcentagemCarteira.toFixed(1)}%)</span>
                      </div>
                      
                      <div className="ativo-progress">
                        <div className="progress-bar acao">
                          <div 
                            className="progress-fill acao" 
                            style={{ width: `${Math.min(porcentagemCarteira, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* FIIs */}
          <div className="card">
            <h2>FIIs ({fiis.length})</h2>
            {carregando ? (
              <div className="loading-indicator">
                <p>Carregando FIIs...</p>
              </div>
            ) : fiis.length === 0 ? (
              <div className="empty-state">
                <p>Nenhum FII encontrado. Adicione seu primeiro FII!</p>
              </div>
            ) : (
              <div className="ativos-container">
                {fiis.map((ativo, index) => {
                  const valorAtivo = ativo.preco * ativo.quantidade;
                  const porcentagemCarteira = valorTotal > 0 ? (valorAtivo / valorTotal) * 100 : 0;
                  
                  return (
                    <div key={ativo.id || index} className="ativo-card fii">
                      <div className="ativo-header">
                        <div className="ativo-info">
                          <h3 className="ativo-codigo">{ativo.codigo}</h3>
                          <p className="ativo-nome">{ativo.nome}</p>
                        </div>
                        <button 
                          className="btn-delete-card"
                          onClick={() => handleRemoverAtivo(ativo.id)}
                          title="Remover ativo"
                        >
                          🗑️
                        </button>
                      </div>
                      
                      <div className="ativo-detalhes">
                        <div className="ativo-quantidade">
                          <span className="ativo-label">Quantidade</span>
                          <input
                            type="number"
                            value={ativo.quantidade}
                            onChange={(e) => handleAtualizarQuantidade(ativo.id, parseInt(e.target.value))}
                            className="quantidade-input"
                            min="0"
                          />
                        </div>
                        <div className="ativo-preco">
                          <span className="ativo-label">Preço</span>
                          <span className="ativo-valor">R$ {ativo.preco.toFixed(2)}</span>
                        </div>
                      </div>
                      
                      <div className="ativo-valor-total">
                        <span className="valor-total">R$ {valorAtivo.toFixed(2)}</span>
                        <span className="porcentagem">({porcentagemCarteira.toFixed(1)}%)</span>
                      </div>
                      
                      <div className="ativo-progress">
                        <div className="progress-bar fii">
                          <div 
                            className="progress-fill fii" 
                            style={{ width: `${Math.min(porcentagemCarteira, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>


        {/* Modal Adicionar Ativo */}
        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3 className="modal-title">Adicionar Ativo</h3>
                <button className="modal-close" onClick={() => setShowModal(false)}>
                  ×
                </button>
              </div>
              
              <div className="form-group">
                <label className="form-label">Código do Ativo *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Ex: PETR4, ITUB4, MXRF11, HGLG11"
                  value={novoAtivo.codigo}
                  onChange={(e) => setNovoAtivo({...novoAtivo, codigo: e.target.value.toUpperCase()})}
                  autoFocus
                />
                <small className="form-help">
                  O nome, tipo e preço serão buscados automaticamente pela API
                </small>
              </div>
              
              <div className="form-group">
                <label className="form-label">Quantidade</label>
                <input
                  type="number"
                  className="form-input"
                  placeholder="0"
                  min="0"
                  value={novoAtivo.quantidade}
                  onChange={(e) => setNovoAtivo({...novoAtivo, quantidade: e.target.value})}
                />
                <small className="form-help">
                  Quantidade inicial do ativo (opcional)
                </small>
              </div>
              
              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button className="btn-primary" onClick={handleAdicionarAtivo}>
                  Adicionar
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Carteira;