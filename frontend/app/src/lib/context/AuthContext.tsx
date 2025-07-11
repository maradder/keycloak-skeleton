import React, { createContext, useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi';


const AuthContext = createContext<{
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any;
  loading: boolean;
  error: string | null;
} | null>(null);


export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const api = useApi();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/auth/protected-endpoint');
        setData(response.data);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [api]);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: {error}</div>;


  return (
    <AuthContext.Provider value={{ data, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
