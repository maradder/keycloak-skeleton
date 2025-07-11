import {useAuth} from '../../lib/hooks/useAuthContext';

export default function Dashboard() {
  const { data } = useAuth();
  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <div className="dashboard-content">
        <h3>Protected Data from the Backend:</h3>
        <pre className="dashboard-data-display">
          {
            Object.entries(data || {})
              .map(([key, value]) => `${key}: ${JSON.stringify(value, null, 2)}`)
              .join('\n')
          }
        </pre>
      </div>
    </div>
  );
};