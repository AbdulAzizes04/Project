import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, UserPlus, User, Mail, Phone, Lock, AlertCircle, CheckCircle2 } from 'lucide-react';

export const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      return setError('Passwords do not match');
    }
    if (formData.password.length < 6) {
      return setError('Password must be at least 6 characters');
    }

    setSubmitting(true);
    try {
      await register({
        full_name: formData.full_name,
        email: formData.email,
        phone: formData.phone || undefined,
        password: formData.password,
        role: 'citizen',
      });
      // Automatic login after registration
      await login(formData.email, formData.password);
      navigate('/citizen');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please check details.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: '2.5rem auto', padding: '0 1rem' }} className="animate-fade-in">
      <div className="glass-card" style={{ padding: '2.5rem 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 12,
            background: 'var(--accent-gradient)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '0.75rem',
            boxShadow: '0 4px 14px rgba(245,158,11,0.4)',
          }}>
            <UserPlus size={24} color="#fff" />
          </div>
          <h2 style={{ fontSize: '1.6rem', marginBottom: '0.25rem' }}>Citizen Registration</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Create an account to lodge grievances and track resolution in real-time
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

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                required
                name="full_name"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="Ramesh Sharma"
                value={formData.full_name}
                onChange={handleChange}
              />
              <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                name="email"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="ramesh@gmail.com"
                value={formData.email}
                onChange={handleChange}
              />
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Mobile Number</label>
            <div style={{ position: 'relative' }}>
              <input
                type="tel"
                name="phone"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="9876543210"
                value={formData.phone}
                onChange={handleChange}
              />
              <Phone size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                name="password"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="Minimum 6 characters"
                value={formData.password}
                onChange={handleChange}
              />
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                name="confirmPassword"
                className="form-input"
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="Confirm password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.75rem' }}
          >
            <UserPlus size={18} />
            {submitting ? 'Registering...' : 'Create Citizen Account'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#818cf8', fontWeight: 600 }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
