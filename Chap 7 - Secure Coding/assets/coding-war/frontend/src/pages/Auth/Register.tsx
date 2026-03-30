import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, type RegisterFormData } from '../../utils/validation';
import { authAPI } from '../../api/endpoints/auth';

function getPasswordStrength(password: string): { score: number; label: string } {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  return { score, label: labels[score] || '' };
}

export default function Register() {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const watchPassword = watch('password', '');
  const strength = useMemo(() => getPasswordStrength(watchPassword), [watchPassword]);

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      await authAPI.register(data);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
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
          <h2>Sign up</h2>

          {success ? (
            <div className="auth-card">
              <div className="status-box">
                <div className="status-icon">✉️</div>
                <h3>Registration Successful</h3>
                <p style={{ color: '#666', fontSize: 13, margin: '8px 0 16px' }}>
                  Your account has been created. You can now log in.
                </p>
                <Link to="/login" className="btn btn-primary btn-sm">Go to login</Link>
              </div>
            </div>
          ) : (
            <div className="auth-card">
              <form onSubmit={handleSubmit(onSubmit)} className="form-stack">
                {error && <div className="alert alert-error">{error}</div>}

                <div className="form-group">
                  <label htmlFor="reg-username" className="form-label">Username</label>
                  <input
                    id="reg-username"
                    type="text"
                    className={`form-input ${errors.username ? 'error' : ''}`}
                    placeholder="3-20 alphanumeric characters"
                    {...register('username')}
                    disabled={isLoading}
                    autoComplete="username"
                  />
                  {errors.username && <span className="form-error">{errors.username.message}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="reg-email" className="form-label">Email</label>
                  <input
                    id="reg-email"
                    type="email"
                    className={`form-input ${errors.email ? 'error' : ''}`}
                    placeholder="you@example.com"
                    {...register('email')}
                    disabled={isLoading}
                    autoComplete="email"
                  />
                  {errors.email && <span className="form-error">{errors.email.message}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="reg-password" className="form-label">Password</label>
                  <input
                    id="reg-password"
                    type="password"
                    className={`form-input ${errors.password ? 'error' : ''}`}
                    placeholder="Min 8 chars, mixed case + number"
                    {...register('password')}
                    disabled={isLoading}
                    autoComplete="new-password"
                  />
                  {watchPassword && (
                    <>
                      <div className="password-strength">
                        {[1, 2, 3, 4].map((i) => (
                          <div
                            key={i}
                            className={`password-strength-bar${i <= strength.score ? ' active' : ''}${strength.score >= 3 ? ' strong' : strength.score >= 2 ? ' medium' : ''}`}
                          />
                        ))}
                      </div>
                      <div className="password-strength-text">{strength.label}</div>
                    </>
                  )}
                  {errors.password && <span className="form-error">{errors.password.message}</span>}
                </div>

                <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                  {isLoading ? <><span className="spinner"></span> Creating...</> : 'Sign up'}
                </button>
              </form>
            </div>
          )}

          <div className="auth-footer">
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
