import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { resetPasswordSchema, type ResetPasswordFormData } from '../../utils/validation';
import { authAPI } from '../../api/endpoints/auth';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = searchParams.get('token');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      await authAPI.resetPassword(token, data.password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Reset failed. The link may be expired.');
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
          <h2>Reset password</h2>

          {!token ? (
            <div className="auth-card">
              <div className="status-box">
                <div className="status-icon">⚠️</div>
                <h3>Invalid Reset Link</h3>
                <p style={{ color: '#666', fontSize: 13, margin: '8px 0 16px' }}>
                  This password reset link is invalid or missing.
                </p>
                <Link to="/forgot-password" className="btn btn-primary btn-sm">Request new link</Link>
              </div>
            </div>
          ) : success ? (
            <div className="auth-card">
              <div className="status-box">
                <div className="status-icon">✅</div>
                <h3>Password Reset</h3>
                <p style={{ color: '#666', fontSize: 13, margin: '8px 0' }}>
                  Your password has been reset. Redirecting to login...
                </p>
              </div>
            </div>
          ) : (
            <div className="auth-card">
              <form onSubmit={handleSubmit(onSubmit)} className="form-stack">
                {error && <div className="alert alert-error">{error}</div>}

                <div className="form-group">
                  <label htmlFor="reset-password" className="form-label">New Password</label>
                  <input
                    id="reset-password"
                    type="password"
                    className={`form-input ${errors.password ? 'error' : ''}`}
                    placeholder="Min 8 chars, mixed case + number"
                    {...register('password')}
                    disabled={isLoading}
                  />
                  {errors.password && <span className="form-error">{errors.password.message}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="reset-confirm" className="form-label">Confirm Password</label>
                  <input
                    id="reset-confirm"
                    type="password"
                    className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                    {...register('confirmPassword')}
                    disabled={isLoading}
                  />
                  {errors.confirmPassword && <span className="form-error">{errors.confirmPassword.message}</span>}
                </div>

                <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                  {isLoading ? <><span className="spinner"></span> Resetting...</> : 'Reset password'}
                </button>
              </form>
            </div>
          )}

          <div className="auth-footer">
            <Link to="/login">Back to login</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
