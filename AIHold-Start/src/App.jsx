import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { inicializarDadosDemo } from './services/apiService';
import { authService } from './services/auth';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Carteira from './pages/Carteira/Carteira';
import Configuracao from './pages/Configuracao/Configuracao';
import Investir from './pages/Investir/Investir';
import './App.css';

// Componente para proteger rotas
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          await authService.getCurrentUser();
          setIsAuthenticated(true);
        } catch (error) {
          setIsAuthenticated(false);
        }
      } else {
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Carregando...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  useEffect(() => {
    // Inicializa dados de demonstração quando a aplicação carrega (apenas se autenticado)
    if (authService.isAuthenticated()) {
      inicializarDadosDemo();
    }
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Navigate to="/carteira" replace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/carteira"
            element={
              <ProtectedRoute>
                <Carteira />
              </ProtectedRoute>
            }
          />
          <Route
            path="/configuracao"
            element={
              <ProtectedRoute>
                <Configuracao />
              </ProtectedRoute>
            }
          />
          <Route
            path="/investir"
            element={
              <ProtectedRoute>
                <Investir />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
