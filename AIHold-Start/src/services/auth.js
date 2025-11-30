import api from './api';

/**
 * Serviço de autenticação
 */
export const authService = {
  /**
   * Registra um novo usuário
   */
  async register(username, email, password) {
    try {
      const data = await api.post('/api/auth/register', {
        username,
        email,
        password,
      });
      
      // Fazer login automaticamente após registro
      if (data) {
        const loginData = await this.login(username, password);
        return loginData;
      }
      
      return data;
    } catch (error) {
      console.error('Erro ao registrar:', error);
      throw error;
    }
  },

  /**
   * Faz login e retorna token
   */
  async login(username, password) {
    try {
      // FastAPI usa form-data para login OAuth2
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao fazer login');
      }
      
      const data = await response.json();
      
      // Salvar token no localStorage
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({ username }));
      }
      
      return data;
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      throw error;
    }
  },

  /**
   * Faz logout
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  /**
   * Verifica se o usuário está autenticado
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  /**
   * Obtém informações do usuário atual
   */
  async getCurrentUser() {
    try {
      const data = await api.get('/api/auth/me');
      return data;
    } catch (error) {
      console.error('Erro ao obter usuário:', error);
      // Se não conseguir, limpar token
      this.logout();
      throw error;
    }
  },
};

export default authService;

