import React from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { Link } from 'react-router-dom';

const NavigationBar: React.FC = () => {
  const { keycloak } = useKeycloak();

  const handleLogout = async () => {
    try {
      const api_base_url = import.meta.env.VITE_API_BASE_URL || "";
      if (api_base_url && keycloak.token) {
        try {
          await fetch(`${api_base_url}/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${keycloak.token}`,
              'Content-Type': 'application/json',
            },
          });
        } catch (error) {
          console.warn('Backend logout failed:', error);
        }
      }

      await keycloak.logout({
        redirectUri: window.location.origin,
      });
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <nav className="navigation-bar">
      <div className="navigation-links">
        <Link to="/dashboard" className="navigation-link">
          Dashboard
        </Link>
        <Link to="/profile" className="navigation-link">
          Profile
        </Link>
      </div>
      
      <div className="navigation-user-section">
        <span>Welcome, {keycloak.tokenParsed?.preferred_username || 'User'}</span>
        <button 
          onClick={handleLogout}
          className="navigation-logout-button"
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default NavigationBar;