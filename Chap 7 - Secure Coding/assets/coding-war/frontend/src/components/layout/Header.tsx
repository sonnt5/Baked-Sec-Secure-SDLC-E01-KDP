import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export default function Header() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuthStore();

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          Coding War
        </Link>

        <nav className="navbar-nav">
          <Link to="/" className={isActive('/') ? 'active' : ''}>Home</Link>
          <Link to="/problems" className={isActive('/problems') ? 'active' : ''}>Problems</Link>
          <Link to="/contests" className={isActive('/contests') ? 'active' : ''}>Contests</Link>
          {isAuthenticated && (
            <Link to="/submissions" className={isActive('/submissions') ? 'active' : ''}>Submissions</Link>
          )}
          {user?.role === 'ADMIN' && (
            <Link to="/admin" className={isActive('/admin') ? 'active' : ''}>Admin</Link>
          )}
        </nav>

        <div className="navbar-actions">
          {isAuthenticated ? (
            <div className="navbar-user">
              <Link to={`/users/${user?.id}`} className="navbar-user-name" style={{ textDecoration: 'none' }}>{user?.username}</Link>
              <span className="navbar-user-role">{user?.role}</span>
              <button className="btn-ghost btn-sm" onClick={handleLogout} style={{ fontSize: 12, padding: '3px 8px', cursor: 'pointer' }}>
                Log out
              </button>
            </div>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link to="/register">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
