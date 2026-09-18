import React from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Menu, 
  Search, 
  ShieldCheck, 
  Sparkles,
  Bot,
  Bell
} from 'lucide-react';
import { NotificationBell } from './NotificationBell';

export const TopHeader = ({ onToggleSidebar }) => {
  const { user, isAuthenticated, isAdmin, isStaff } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Helper to determine active page title
  const getPageTitle = () => {
    const p = location.pathname;
    if (p === '/') return 'Public Grievance Redressal Portal';
    if (p === '/admin') return 'Admin Executive Dashboard';
    if (p.startsWith('/admin/complaints')) return 'Civic Complaints Management';
    if (p === '/admin/analytics') return 'Grievance Analytics & SLA Intelligence';
    if (p === '/admin/models') return 'AI Model Evaluation & Viva Metrics';
    if (p === '/admin/departments') return 'Municipal Departments & SLA Routing';
    if (p === '/admin/users') return 'User & Role Access Management';
    if (p === '/staff') return 'Staff Field Work Orders';
    if (p === '/citizen') return 'Citizen Grievance Redressal Portal';
    if (p === '/chat') return 'AI Grievance Assistant';
    if (p === '/track') return 'Real-Time Complaint Tracker';
    if (p.startsWith('/complaints/')) return 'Complaint Case Dossier';
    if (p === '/login') return 'Citizen & Officer Authentication';
    if (p === '/register') return 'Citizen Account Registration';
    return 'LokSeva AI Redressal';
  };

  return (
    <header className="top-header">
      <div className="top-header-left">
        <button
          onClick={onToggleSidebar}
          className="menu-toggle-btn"
          aria-label="Toggle navigation menu"
          title="Open Menu"
        >
          <Menu size={20} />
        </button>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {getPageTitle()}
            </h2>
            <span style={{
              background: 'var(--primary-50)',
              color: 'var(--primary-600)',
              border: '1px solid var(--primary-100)',
              borderRadius: 20,
              fontSize: '0.68rem',
              fontWeight: 700,
              padding: '0.15rem 0.5rem',
              letterSpacing: '0.04em',
              textTransform: 'uppercase'
            }}>
              GovTech AI
            </span>
          </div>
          <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
            National e-Governance Delivery Assessment (NeSDA) Compliant
          </span>
        </div>
      </div>

      <div className="top-header-right">
        {/* Quick Track Link */}
        <Link
          to="/track"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            background: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-subtle)',
            padding: '0.45rem 0.85rem',
            borderRadius: 20,
            fontSize: '0.82rem',
            color: 'var(--text-secondary)',
            fontWeight: 500,
            transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--primary-500)';
            e.currentTarget.style.color = 'var(--primary-600)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-subtle)';
            e.currentTarget.style.color = 'var(--text-secondary)';
          }}
        >
          <Search size={14} />
          <span>Track Ticket</span>
        </Link>

        {/* Notifications */}
        {isAuthenticated && <NotificationBell />}

        {/* User Pill / Login CTA */}
        {isAuthenticated ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            background: '#ffffff',
            padding: '0.35rem 0.75rem',
            borderRadius: 30,
            border: '1px solid var(--border-subtle)',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div style={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              background: 'var(--primary-50)',
              border: '1px solid var(--primary-200)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--primary-600)',
              fontSize: '0.8rem',
              fontWeight: 700
            }}>
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.1 }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {user?.full_name?.split(' ')[0]}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                {user?.role}
              </span>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Link to="/login" className="btn btn-secondary btn-sm">
              Sign In
            </Link>
            <Link to="/register" className="btn btn-primary btn-sm">
              Register
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
