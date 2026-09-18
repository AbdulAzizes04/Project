import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, LogIn, Lock, Mail, AlertCircle } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const loggedUser = await login(email, password);
      if (from !== '/') {
        navigate(from, { replace: true });
      } else if (loggedUser.role === 'admin') {
        navigate('/admin', { replace: true });
      } else if (loggedUser.role === 'staff') {
        navigate('/staff', { replace: true });
      } else {
        navigate('/citizen', { replace: true });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemo = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError('');
  };

  return (
    <div style={{ maxWidth: 460, margin: '3rem auto', padding: '0 1rem' }} className="animate-fade-in">
      <div className="glass-card" style={{ padding: '2.5rem 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 12,
            background: 'var(--primary-gradient)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '0.75rem',
            boxShadow: '0 4px 14px rgba(79,70,229,0.4)',
          }}>
            <Bot size={28} color="#fff" />
          </div>
          <h2 style={{ fontSize: '1.6rem', marginBottom: '0.25rem' }}>Welcome Back</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Sign in to access your grievance portal account
          </p>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 10,
            padding: '0.75rem 1rem',
            color: '#fca5a5',
            fontSize: '0.85rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Demo Credentials Quick Fill Pills */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
            QUICK DEMO LOGINS (CLICK TO AUTO-FILL):
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="demo-pill"
              onClick={() => fillDemo('admin@gov.in', 'Admin@123')}
            >
              👑 Admin / TPO
            </button>
            <button
              type="button"
              className="demo-pill"
              onClick={() => fillDemo('staff.water@gov.in', 'Staff@123')}
            >
              🛠️ Water Staff
            </button>
            <button
              type="button"
              className="demo-pill"
              onClick={() => fillDemo('ramesh.sharma@gmail.com', 'Citizen@123')}
            >
              👤 Citizen
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem' }}
          >
            <LogIn size={18} />
            {submitting ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: '1.75rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: '#818cf8', fontWeight: 600 }}>
            Register as Citizen
          </Link>
        </div>
      </div>
    </div>
  );
};
