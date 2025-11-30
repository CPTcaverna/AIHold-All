import { useLocation, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    {
      path: '/carteira',
      label: 'Carteira',
      icon: '💼'
    },
    {
      path: '/configuracao',
      label: 'Configurações',
      icon: '⚙️'
    },
    {
      path: '/investir',
      label: 'Investir',
      icon: '📈'
    }
  ];

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <ul className="nav-list">
        {navItems.map((item) => (
          <li
            key={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </li>
        ))}
        <li className="nav-item logout" onClick={handleLogout}>
          <span className="nav-icon">🚪</span>
          Sair
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
