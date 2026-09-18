import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Search, MessageSquare, Video,
  Database, Info, Shield, Activity, User, Wifi
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard & Analytics', icon: LayoutDashboard },
  { path: '/pipeline', label: 'Search & Gait Pipeline', icon: Search },
  { path: '/chatbot', label: 'AI Forensic Chatbot', icon: MessageSquare },
  { path: '/player', label: 'CCTV Video Player', icon: Video },
  { path: '/cases', label: 'SQLite Case Logs', icon: Database },
  { path: '/about', label: 'About This Project', icon: Info },
];

export default function Sidebar() {
  return (
    <aside
      className="flex flex-col h-screen"
      style={{
        width: 260,
        minWidth: 260,
        background: 'linear-gradient(180deg, #050b18 0%, #0a1628 100%)',
        borderRight: '1px solid #1a2a4a',
        flexShrink: 0,
      }}
    >
      {/* ── Logo ──────────────────────────────────────────────────────── */}
      <div className="px-5 pt-6 pb-4" style={{ borderBottom: '1px solid #1a2a4a' }}>
        <div className="flex items-center gap-3 mb-1">
          <div
            className="flex items-center justify-center rounded-lg"
            style={{
              width: 36, height: 36,
              background: 'linear-gradient(135deg, #00d4ff22, #0066ff33)',
              border: '1px solid #00d4ff44',
            }}
          >
            <Shield size={18} color="#00d4ff" />
          </div>
          <div>
            <div
              style={{
                fontSize: 14, fontWeight: 800, letterSpacing: '0.08em',
                color: '#00d4ff', lineHeight: 1.2,
              }}
            >
              VISIONTRACE AI
            </div>
            <div style={{ fontSize: 9, color: '#4a5568', letterSpacing: '0.06em', fontWeight: 500 }}>
              AI FORENSIC INTELLIGENCE
            </div>
          </div>
        </div>
      </div>

      {/* ── Navigation ────────────────────────────────────────────────── */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div style={{ fontSize: 10, color: '#4a5568', letterSpacing: '0.1em', fontWeight: 600, marginBottom: 8, paddingLeft: 4 }}>
          MODULES
        </div>
        <div className="space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `sidebar-nav-item ${isActive ? 'active' : ''}`
              }
            >
              <Icon size={16} />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* ── System Status ─────────────────────────────────────────────── */}
      <div
        className="px-4 py-4"
        style={{ borderTop: '1px solid #1a2a4a' }}
      >
        <div style={{ fontSize: 10, color: '#4a5568', letterSpacing: '0.1em', fontWeight: 600, marginBottom: 10 }}>
          SYSTEM STATUS
        </div>

        <div className="flex items-center gap-2 mb-3">
          <div
            className="rounded-full"
            style={{
              width: 8, height: 8,
              background: '#00ff88',
              boxShadow: '0 0 8px #00ff88',
              animation: 'pulse 2s infinite',
            }}
          />
          <span style={{ fontSize: 12, color: '#00ff88', fontWeight: 600 }}>SYSTEM ONLINE</span>
          <Wifi size={12} color="#00ff8866" />
        </div>

        <div className="flex items-center gap-2 mb-4">
          <Activity size={12} color="#00d4ff" />
          <span style={{ fontSize: 11, color: '#94a3b8' }}>AI Pipeline Ready</span>
        </div>

        {/* Investigator Profile */}
        <div
          className="flex items-center gap-3 p-3 rounded-lg"
          style={{ background: '#0f1f3d', border: '1px solid #1a2a4a' }}
        >
          <div
            className="flex items-center justify-center rounded-full flex-shrink-0"
            style={{ width: 32, height: 32, background: '#00d4ff22', border: '1px solid #00d4ff44' }}
          >
            <User size={14} color="#00d4ff" />
          </div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#e2e8f0' }}>Investigator</div>
            <div style={{ fontSize: 10, color: '#4a5568' }}>Admin Access</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
