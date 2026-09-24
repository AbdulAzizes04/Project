import React, { useState } from 'react';
import { Search, Bell, ChevronDown, LogOut, User, Settings } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { initials, clsx } from '@/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface TopNavbarProps {
  sidebarCollapsed: boolean;
}

const TopNavbar: React.FC<TopNavbarProps> = ({ sidebarCollapsed }) => {
  const { user, logout } = useAuth();
  const [searchOpen, setSearchOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  const notifications = [
    { id: 1, text: 'Oceanic Shipping Ltd. classified as HIGH RISK', time: '2m ago', unread: true },
    { id: 2, text: 'New dataset uploaded and processed', time: '1h ago', unread: true },
    { id: 3, text: 'Model retraining completed — XGBoost 92.6% acc', time: '3h ago', unread: false },
    { id: 4, text: 'Network risk alert: 3 new elevated nodes', time: '1d ago', unread: false },
  ];
  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header
      className="h-16 bg-white border-b border-surface-200 flex items-center justify-between px-6 fixed top-0 right-0 z-20 transition-all duration-250"
      style={{ left: sidebarCollapsed ? 64 : 260 }}
    >
      {/* Left: Page context */}
      <div className="flex items-center gap-3">
        {searchOpen ? (
          <motion.div initial={{ width: 0, opacity: 0 }} animate={{ width: 280, opacity: 1 }} className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-content-tertiary" />
            <input
              autoFocus
              placeholder="Search companies, predictions..."
              onBlur={() => setSearchOpen(false)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-surface-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </motion.div>
        ) : (
          <button
            onClick={() => setSearchOpen(true)}
            className="nav-icon-btn"
            aria-label="Search"
          >
            <Search className="w-4.5 h-4.5" />
          </button>
        )}
      </div>

      {/* Right: Notifications + Profile */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setNotifOpen(n => !n); setProfileOpen(false); }}
            className="nav-icon-btn relative"
            aria-label="Notifications"
          >
            <Bell className="w-4.5 h-4.5" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-danger text-white text-2xs font-bold rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
          <AnimatePresence>
            {notifOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-11 w-80 bg-white rounded-xl shadow-dropdown border border-surface-200 z-50"
              >
                <div className="p-4 border-b border-surface-200">
                  <p className="text-sm font-semibold text-content-primary">Notifications</p>
                </div>
                <div className="py-1">
                  {notifications.map(n => (
                    <div key={n.id} className={clsx('px-4 py-3 hover:bg-surface-50 cursor-pointer', n.unread && 'bg-primary-light/40')}>
                      <p className="text-xs text-content-primary">{n.text}</p>
                      <p className="text-2xs text-content-tertiary mt-0.5">{n.time}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Profile */}
        <div className="relative">
          <button
            onClick={() => { setProfileOpen(p => !p); setNotifOpen(false); }}
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-surface-100 transition-colors"
          >
            <div className="w-7 h-7 bg-primary rounded-full flex items-center justify-center text-white text-xs font-bold">
              {user ? initials(user.name) : 'U'}
            </div>
            <div className="text-left hidden md:block">
              <p className="text-xs font-semibold text-content-primary leading-none">{user?.name || 'User'}</p>
              <p className="text-2xs text-content-tertiary capitalize">{user?.role || 'analyst'}</p>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-content-tertiary" />
          </button>
          <AnimatePresence>
            {profileOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-11 w-48 bg-white rounded-xl shadow-dropdown border border-surface-200 z-50 py-1"
              >
                <button className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-content-secondary hover:bg-surface-50 hover:text-content-primary">
                  <User className="w-4 h-4" /> Profile
                </button>
                <button className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-content-secondary hover:bg-surface-50 hover:text-content-primary">
                  <Settings className="w-4 h-4" /> Settings
                </button>
                <div className="border-t border-surface-200 mt-1 pt-1">
                  <button
                    onClick={logout}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-danger hover:bg-danger-light"
                  >
                    <LogOut className="w-4 h-4" /> Sign Out
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
};

export default TopNavbar;
