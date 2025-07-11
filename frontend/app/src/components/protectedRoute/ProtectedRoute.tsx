import React from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { AuthProvider } from '../../lib/context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) {
    return <div>Loading...</div>;
  }

  if (!keycloak.authenticated) {
    return <div>Not authenticated. Redirecting to login...</div>;
  }

  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
};

export default ProtectedRoute;