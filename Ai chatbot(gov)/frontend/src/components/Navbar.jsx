import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Bot, 
  ShieldAlert, 
  LayoutDashboard, 
  FileText, 
  BarChart3, 
  Cpu, 
  LogOut, 
  User as UserIcon,
  Search
} from 'lucide-react';
import { NotificationBell } from './NotificationBell';

export const Navbar = () => {
  const { user, isAuthenticated, logout, isAdmin, isStaff } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="navbar">
      <Link to="/" className="navbar-brand">
        <div style={{
          width: 38,
          height: 38,
          borderRadius: 10,
          background: 'var(--primary-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(79,70,229,0.4)'
        }}>
          <Bot size={22} color="#fff" />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ letterSpacing: '-0.03em', lineHeight: 1.1 }}>LokSeva<span style={{ color: '#818cf8' }}>AI</span></span>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Public Grievance Redressal</span>
        </div>
        <span className="brand-badge">GovTech AI</span>
      </Link>

      <nav className="navbar-links">
        <Link to="/track" className={`nav-item ${location.pathname === '/track' ? 'active' : ''}`}>
          <Search size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
          Track Complaint
        </Link>

        {isAuthenticated && !isAdmin && !isStaff && (
          <>
            <Link to="/citizen" className={`nav-item ${location.pathname === '/citizen' ? 'active' : ''}`}>
              <LayoutDashboard size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              My Grievances
            </Link>
            <Link to="/chat" className={`nav-item ${location.pathname === '/chat' ? 'active' : ''}`}>
              <Bot size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              AI Grievance Assistant
            </Link>
          </>
        )}

        {isAdmin && (
          <>
            <Link to="/admin" className={`nav-item ${location.pathname === '/admin' ? 'active' : ''}`}>
              <LayoutDashboard size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              Overview
            </Link>
            <Link to="/admin/complaints" className={`nav-item ${location.pathname.startsWith('/admin/complaints') ? 'active' : ''}`}>
              <FileText size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              Complaints
            </Link>
            <Link to="/admin/analytics" className={`nav-item ${location.pathname === '/admin/analytics' ? 'active' : ''}`}>
              <BarChart3 size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              Analytics
            </Link>
            <Link to="/admin/models" className={`nav-item ${location.pathname === '/admin/models' ? 'active' : ''}`}>
              <Cpu size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
              AI Models
            </Link>
          </>
        )}

        {isStaff && (
          <Link to="/staff" className={`nav-item ${location.pathname === '/staff' ? 'active' : ''}`}>
            <ShieldAlert size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: -2 }} />
            Assigned Queue
          </Link>
        )}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {isAuthenticated ? (
          <>
            <NotificationBell />
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              background: 'rgba(255,255,255,0.05)',
              padding: '0.4rem 0.8rem',
              borderRadius: 30,
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: 'rgba(99,102,241,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#818cf8'
              }}>
                <UserIcon size={16} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.1 }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user?.full_name?.split(' ')[0]}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                  {user?.role}
                </span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="btn btn-secondary btn-sm"
              title="Sign out"
            >
              <LogOut size={15} />
            </button>
          </>
        ) : (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
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
