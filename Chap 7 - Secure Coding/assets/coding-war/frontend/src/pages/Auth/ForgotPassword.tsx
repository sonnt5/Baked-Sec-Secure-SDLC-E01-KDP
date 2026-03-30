import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../../utils/validation';
import { authAPI } from '../../api/endpoints/auth';

export default function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      await authAPI.forgotPassword(data.email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send reset link.');
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

          {success ? (
            <div className="auth-card">
              <div className="status-box">
                <div className="status-icon">✉️</div>
                <h3>Check Your Email</h3>
                <p style={{ color: '#666', fontSize: 13, margin: '8px 0 16px' }}>
                  A password reset link has been sent to your email.
                </p>
                <Link to="/login" className="btn btn-sm">Back to login</Link>
              </div>
            </div>
          ) : (
            <div className="auth-card">
              <p className="subtitle">Enter your email to receive a password reset link.</p>
              <form onSubmit={handleSubmit(onSubmit)} className="form-stack">
                {error && <div className="alert alert-error">{error}</div>}

                <div className="form-group">
                  <label htmlFor="forgot-email" className="form-label">Email</label>
                  <input
                    id="forgot-email"
                    type="email"
                    className={`form-input ${errors.email ? 'error' : ''}`}
                    placeholder="you@example.com"
                    {...register('email')}
                    disabled={isLoading}
                  />
                  {errors.email && <span className="form-error">{errors.email.message}</span>}
                </div>

                <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                  {isLoading ? <><span className="spinner"></span> Sending...</> : 'Send reset link'}
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
