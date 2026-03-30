import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginFormData } from '../../utils/validation';
import { authAPI } from '../../api/endpoints/auth';
import { useAuthStore } from '../../stores/authStore';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser, setTokens } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authAPI.login(data);
      setUser(response.user);
      setTokens(response.accessToken, response.refreshToken);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-nav">
        <div className="auth-nav-inner">
          <Link to="/">Coding War</Link>
        </div>
      </div>
      <div className="auth-container">
        <div className="auth-box">
          <h2>Log in</h2>
          <div className="auth-card">
            <form onSubmit={handleSubmit(onSubmit)} className="form-stack">
              {error && <div className="alert alert-error">{error}</div>}

              <div className="form-group">
                <label htmlFor="login-email" className="form-label">Email or Username</label>
                <input
                  id="login-email"
                  type="text"
                  className={`form-input ${errors.email ? 'error' : ''}`}
                  placeholder="you@example.com"
                  {...register('email')}
                  disabled={isLoading}
                  autoComplete="username"
                />
                {errors.email && <span className="form-error">{errors.email.message}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="login-password" className="form-label">Password</label>
                <input
                  id="login-password"
                  type="password"
                  className={`form-input ${errors.password ? 'error' : ''}`}
                  {...register('password')}
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                {errors.password && <span className="form-error">{errors.password.message}</span>}
              </div>

              <div style={{ fontSize: 12, textAlign: 'right', marginBottom: 8 }}>
                <Link to="/forgot-password">Forgot password?</Link>
              </div>

              <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                {isLoading ? <><span className="spinner"></span> Logging in...</> : 'Log in'}
              </button>
            </form>
          </div>
          <div className="auth-footer">
            Don't have an account? <Link to="/register">Sign up</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
