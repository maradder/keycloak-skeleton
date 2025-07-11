import {useAuth} from '../../lib/hooks/useAuthContext';

const UserProfile = () => {
  const { data } = useAuth();

  return (
    <div className="user-profile-container">
      <h2>User Profile</h2>
      <div className="user-profile-info">
        <h3>User Information: {data.user.username}</h3>
      </div>
    </div>
  );
};

export default UserProfile;
