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

    // Response interceptor to handle token refresh and errors
    instance.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized - token expired or invalid
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
            return Promise.reject(error);
          }
        }

        // Handle network errors
        if (!error.response) {
          error.message = 'Network error: Unable to connect to server';
        } else {
          // Handle other HTTP errors
          const status = error.response.status;
          switch (status) {
            case 403:
              error.message = 'Access denied: Insufficient permissions';
              break;
            case 404:
              error.message = 'Resource not found';
              break;
            case 500:
              error.message = 'Server error: Please try again later';
              break;
            case 503:
              error.message = 'Service unavailable: Server is temporarily down';
              break;
            default:
              error.message = error.response.data?.detail || 
                            error.response.data?.message || 
                            `HTTP ${status}: ${error.message}`;
          }
        }

        return Promise.reject(error);
      }
    );

    return instance;
  }, [keycloak]);

  return api;
};