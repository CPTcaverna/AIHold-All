// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Função para obter o token do localStorage
const getToken = () => {
  return localStorage.getItem('token');
};

// Função para fazer requisições HTTP
const apiRequest = async (endpoint, options = {}) => {
  const token = getToken();
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    ...options,
  };

  try {
    console.log(`[API] Fazendo requisição para: ${url}`);
    console.log(`[API] Método: ${defaultOptions.method || 'GET'}`);
    console.log(`[API] Token presente: ${!!token}`);
    
    const response = await fetch(url, defaultOptions);
    
    console.log(`[API] Resposta recebida: ${response.status} ${response.statusText}`);
    
    // Se não tiver conteúdo, retornar null
    if (response.status === 204) {
      return null;
    }
    
    // Tentar fazer parse do JSON, mas pode não ter corpo em alguns erros
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = { detail: `HTTP error! status: ${response.status}` };
    }
    
    if (!response.ok) {
      // Criar erro com mais informações
      const error = new Error(data.detail || data.message || `HTTP error! status: ${response.status}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('[API] Erro na requisição:', error);
    console.error('[API] URL tentada:', url);
    console.error('[API] Tipo do erro:', error.name);
    console.error('[API] Mensagem:', error.message);
    
    // Se já é um Error criado por nós, re-lançar
    if (error.status) {
      throw error;
    }
    
    // Tratar erros de rede especificamente
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error(
        `Não foi possível conectar ao servidor. Verifique se o backend está rodando em ${API_BASE_URL}.\n\n` +
        `Para iniciar o backend, execute:\n` +
        `cd AIHold-Back\n` +
        `uvicorn main:app --reload`
      );
    }
    
    // Caso contrário, criar um novo erro
    throw new Error(error.message || 'Erro na comunicação com o servidor');
  }
};

// Métodos HTTP auxiliares
export const api = {
  get: (endpoint) => apiRequest(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  put: (endpoint, data) => apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (endpoint) => apiRequest(endpoint, { method: 'DELETE' }),
};

export default api;

