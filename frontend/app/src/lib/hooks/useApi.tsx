import { useKeycloak } from '@react-keycloak/web';
import axios from 'axios';
import { useMemo } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export const useApi = () => {
  const { keycloak } = useKeycloak();

  const api = useMemo(() => {
    const instance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
	  
    });

    // Request interceptor to add auth token
    instance.interceptors.request.use(
      (config) => {
        if (keycloak.token) {
          config.headers.Authorization = `Bearer ${keycloak.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    instance.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshed = await keycloak.updateToken(30);
            if (refreshed) {
              originalRequest.headers.Authorization = `Bearer ${keycloak.token}`;
              return instance(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            keycloak.login();
          }
        }

        return Promise.reject(error);
      }
    );

    return instance;
  }, [keycloak]);

  return api;
};