import { useKeycloak } from '@react-keycloak/web';
import { useCallback } from 'react';

export const useLogout = () => {
  const { keycloak } = useKeycloak();

  const logout = useCallback(async (options?: { 
    callBackend?: boolean;
    redirectUri?: string;
  }) => {
    const { callBackend = true, redirectUri = window.location.origin } = options || {};

    try {
      // Optionally call backend logout endpoint first
      if (callBackend && keycloak.token) {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
        if (apiBaseUrl) {
          try {
            await fetch(`${apiBaseUrl}/auth/logout-simple`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${keycloak.token}`,
                'Content-Type': 'application/json',
              },
            });
            console.log('Backend logout successful');
          } catch (error) {
            console.warn('Backend logout failed:', error);
            // Continue with frontend logout even if backend fails
          }
        }
      }

      // Logout from Keycloak (this is the crucial part)
      await keycloak.logout({
        redirectUri,
      });
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }, [keycloak]);

  return { logout };
};