import React, { createContext, useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi';

interface AuthData {
  message: string;
  user: {
    id: string;
    username: string;
    email: string;
    roles: string[];
  };
  timestamp: number;
  data: {
    example: string;
    items: string[];
  };
}

interface AuthContextType {
  data: AuthData | null;
  loading: boolean;
  error: string | null;
  retry: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const api = useApi();
  const [data, setData] = useState<AuthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/auth/protected-endpoint');
      setData(response.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Failed to fetch protected data';
      setError(errorMessage);
      console.error('Auth context error:', err);
    } finally {
      setLoading(false);
    }
  };

  const retry = () => {
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, [api]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen">
        <div className="text-red-600 mb-4">Error: {error}</div>
        <button 
          onClick={retry}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ data, loading, error, retry }}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
