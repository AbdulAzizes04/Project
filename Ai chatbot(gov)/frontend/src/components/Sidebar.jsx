import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Cpu,
  Search,
  Bot,
  ShieldAlert,
  Building2,
  Users,
  LogOut,
  User as UserIcon,
  Home,
  CheckCircle2,
  Sparkles,
  ChevronRight,
  X
} from 'lucide-react';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user, isAuthenticated, logout, isAdmin, isStaff } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <>
      {/* Mobile backdrop overlay */}
      <div 
        className={`sidebar-overlay ${isOpen ? 'open' : ''}`} 
        onClick={onClose} 
      />

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-header">
          <Link to="/" className="sidebar-brand" onClick={onClose}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 12,
              background: 'var(--primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
              color: '#ffffff',
            }}>
              <Bot size={24} />
            </div>
            <div>
              <div className="sidebar-brand-title">
                LokSeva<span style={{ color: 'var(--primary-600)' }}>AI</span>
              </div>
              <div className="sidebar-brand-sub">GovTech Portal</div>
            </div>
          </Link>

          {/* Close button for mobile */}
          <button
            onClick={onClose}
            className="menu-toggle-btn"
            style={{ display: isOpen ? 'flex' : 'none' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="sidebar-content">
          {/* Admin Navigation */}
          {isAdmin && (
            <>
              <div>
                <div className="sidebar-section-title">Core Management</div>
                <ul className="sidebar-nav-list">
                  <li>
                    <Link
                      to="/admin"
                      className={`sidebar-link ${location.pathname === '/admin' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <LayoutDashboard size={18} />
                      <span>Overview</span>
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/admin/complaints"
                      className={`sidebar-link ${location.pathname.startsWith('/admin/complaints') ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <FileText size={18} />
                      <span>Complaints</span>
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/chat"
                      className={`sidebar-link ${location.pathname === '/chat' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <Bot size={18} />
                      <span>AI Grievance Assistant</span>
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/track"
                      className={`sidebar-link ${location.pathname === '/track' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <Search size={18} />
                      <span>Track Complaint</span>
                    </Link>
                  </li>
                </ul>
              </div>

              <div>
                <div className="sidebar-section-title">Intelligence & ML</div>
                <ul className="sidebar-nav-list">
                  <li>
                    <Link
                      to="/admin/analytics"
                      className={`sidebar-link ${location.pathname === '/admin/analytics' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <BarChart3 size={18} />
                      <span>Analytics & SLA</span>
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/admin/models"
                      className={`sidebar-link ${location.pathname === '/admin/models' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <Cpu size={18} />
                      <span>AI Models & Viva</span>
                    </Link>
                  </li>
                </ul>
              </div>

              <div>
                <div className="sidebar-section-title">Governance</div>
                <ul className="sidebar-nav-list">
                  <li>
                    <Link
                      to="/admin/departments"
                      className={`sidebar-link ${location.pathname === '/admin/departments' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <Building2 size={18} />
                      <span>Departments</span>
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/admin/users"
                      className={`sidebar-link ${location.pathname === '/admin/users' ? 'active' : ''}`}
                      onClick={onClose}
                    >
                      <Users size={18} />
                      <span>User Management</span>
                    </Link>
                  </li>
                </ul>
              </div>
            </>
          )}

          {/* Staff Navigation */}
          {isStaff && (
            <div>
              <div className="sidebar-section-title">Work Orders</div>
              <ul className="sidebar-nav-list">
                <li>
                  <Link
                    to="/staff"
                    className={`sidebar-link ${location.pathname === '/staff' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <ShieldAlert size={18} />
                    <span>Assigned Queue</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/chat"
                    className={`sidebar-link ${location.pathname === '/chat' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Bot size={18} />
                    <span>AI Assistant</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/track"
                    className={`sidebar-link ${location.pathname === '/track' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Search size={18} />
                    <span>Track Complaint</span>
                  </Link>
                </li>
              </ul>
            </div>
          )}

          {/* Citizen Navigation */}
          {isAuthenticated && !isAdmin && !isStaff && (
            <div>
              <div className="sidebar-section-title">Public Services</div>
              <ul className="sidebar-nav-list">
                <li>
                  <Link
                    to="/citizen"
                    className={`sidebar-link ${location.pathname === '/citizen' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <LayoutDashboard size={18} />
                    <span>My Grievances</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/chat"
                    className={`sidebar-link ${location.pathname === '/chat' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Bot size={18} />
                    <span>Lodge with AI</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/track"
                    className={`sidebar-link ${location.pathname === '/track' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Search size={18} />
                    <span>Track Ticket</span>
                  </Link>
                </li>
              </ul>
            </div>
          )}

          {/* Public / Unauthenticated Navigation */}
          {!isAuthenticated && (
            <div>
              <div className="sidebar-section-title">Portal Access</div>
              <ul className="sidebar-nav-list">
                <li>
                  <Link
                    to="/"
                    className={`sidebar-link ${location.pathname === '/' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Home size={18} />
                    <span>Portal Home</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/track"
                    className={`sidebar-link ${location.pathname === '/track' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <Search size={18} />
                    <span>Track Complaint</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/login"
                    className={`sidebar-link ${location.pathname === '/login' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <UserIcon size={18} />
                    <span>Sign In</span>
                  </Link>
                </li>
                <li>
                  <Link
                    to="/register"
                    className={`sidebar-link ${location.pathname === '/register' ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    <CheckCircle2 size={18} />
                    <span>Register Citizen</span>
                  </Link>
                </li>
              </ul>
            </div>
          )}

          {/* System Badge */}
          <div style={{ marginTop: 'auto', padding: '0.5rem 0.25rem' }}>
            <div style={{
              background: 'var(--primary-50)',
              border: '1px solid var(--primary-100)',
              borderRadius: 12,
              padding: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}>
              <div style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: '#16a34a',
                boxShadow: '0 0 8px #16a34a'
              }} />
              <div style={{ fontSize: '0.74rem', lineHeight: 1.2 }}>
                <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>AI Redressal Engine</div>
                <div style={{ color: 'var(--text-secondary)', marginTop: 2 }}>Online & Active</div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Footer with User Profile */}
        <div className="sidebar-footer">
          {isAuthenticated ? (
            <div className="sidebar-user-card">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 34,
                  height: 34,
                  borderRadius: '50%',
                  background: 'var(--primary-50)',
                  border: '1px solid var(--primary-200)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--primary-600)'
                }}>
                  <UserIcon size={18} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.15 }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {user?.full_name?.split(' ')[0] || 'User'}
                  </span>
                  <span style={{
                    fontSize: '0.7rem',
                    color: 'var(--primary-600)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em'
                  }}>
                    {user?.role}
                  </span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 6,
                  borderRadius: 6,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'color var(--transition-fast)',
                }}
                title="Sign out"
                onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Link to="/login" className="btn btn-secondary btn-sm" style={{ flex: 1, padding: '0.5rem' }}>
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm" style={{ flex: 1, padding: '0.5rem' }}>
                Register
              </Link>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
