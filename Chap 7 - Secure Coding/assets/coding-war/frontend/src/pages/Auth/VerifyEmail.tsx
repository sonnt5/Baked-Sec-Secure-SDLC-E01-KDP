import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { authAPI } from '../../api/endpoints/auth';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link.');
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await authAPI.verifyEmail(token);
        setStatus('success');
        setMessage(response.message || 'Email verified successfully!');
        setTimeout(() => navigate('/login'), 3000);
      } catch (error: any) {
        setStatus('error');
        setMessage(error.response?.data?.message || 'Verification failed. The link may be expired.');
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  return (
    <div className="auth-page">
      <div className="auth-nav">
        <div className="auth-nav-inner">
          <Link to="/">Coding War</Link>
        </div>
      </div>
      <div className="auth-container">
        <div className="auth-box">
          <h2>Email Verification</h2>
          <div className="auth-card">
            <div className="status-box">
              {status === 'loading' && (
                <>
                  <div style={{ marginBottom: 10 }}><span className="spinner" style={{ width: 24, height: 24 }}></span></div>
                  <h3>Verifying your email...</h3>
                  <p style={{ color: '#666', fontSize: 13 }}>Please wait.</p>
                </>
              )}
              {status === 'success' && (
                <>
                  <div className="status-icon">✅</div>
                  <h3>Email Verified!</h3>
                  <p style={{ color: '#666', fontSize: 13 }}>{message}</p>
                  <p style={{ color: '#999', fontSize: 12, marginTop: 8 }}>Redirecting to login...</p>
                </>
              )}
              {status === 'error' && (
                <>
                  <div className="status-icon">❌</div>
                  <h3>Verification Failed</h3>
                  <p style={{ color: '#666', fontSize: 13, marginBottom: 16 }}>{message}</p>
                  <Link to="/login" className="btn btn-primary btn-sm">Go to login</Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
