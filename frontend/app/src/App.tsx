import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ReactKeycloakProvider, useKeycloak } from '@react-keycloak/web';
import Keycloak from 'keycloak-js';
import UserProfile from './pages/userProfile/UserProfile';
import Dashboard from './pages/dashboard/Dashboard';
import ProtectedRoute from './components/protectedRoute/ProtectedRoute';
import Navbar from './components/navbars/NavigationBar';
import './App.css';

function App() {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) {
    return <div>Loading...</div>;
  }

  if (!keycloak.authenticated) {
    return <div>Not authenticated</div>;
  }

  return (
    <div className="App">
      <Router>
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <UserProfile />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
      </Router>
    </div>
  );
}

const keycloak = new Keycloak({
  realm: 'testrealm',
  url: import.meta.env.VITE_AUTH_SERVER_BASE_URL || 'http://localhost:8080',
  clientId: 'test-client-id',
});

const WrappedApp = () => (
  <ReactKeycloakProvider 
    authClient={keycloak} 
    initOptions={{ 
      onLoad: 'login-required',
      checkLoginIframe: false, // Disable iframe checking for simpler logout
    }}
  >
    <App />
  </ReactKeycloakProvider>
);

export default WrappedApp;