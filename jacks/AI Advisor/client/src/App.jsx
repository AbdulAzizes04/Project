import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3, Database, Sparkles, Shield, LogOut, Sun, Moon, Menu, ChevronLeft, ChevronRight, User
} from 'lucide-react';

// Import Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Datasets from './pages/Datasets';
import Chat from './pages/Chat';
import Admin from './pages/Admin';

const App = () => {
  const { token, user, loading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Shared active dataset across views
  const [activeDataset, setActiveDataset] = useState(null);

  // Manage Dark/Light theme classes
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-semibold text-slate-400">Loading AI Advisor...</p>
        </div>
      </div>
    );
  }

  // Route guarding: render Login if no token is present
  if (!token) {
    return <Login />;
  }

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'datasets', label: 'Dataset Workspace', icon: Database },
    { id: 'chat', label: 'AI Chat Advisor', icon: Sparkles }
  ];

  // Expose Admin view only if user is admin
  if (user && user.role === 'admin') {
    navItems.push({ id: 'admin', label: 'Admin Console', icon: Shield });
  }

  const renderView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard activeDataset={activeDataset} />;
      case 'datasets':
        return <Datasets activeDataset={activeDataset} setActiveDataset={setActiveDataset} />;
      case 'chat':
        return <Chat activeDataset={activeDataset} />;
      case 'admin':
        return <Admin />;
      default:
        return <Dashboard activeDataset={activeDataset} />;
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-200">
      {/* Sidebar navigation */}
      <aside
        className={`bg-white dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between transition-all duration-300 z-10 ${
          sidebarCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Top Logo */}
        <div>
          <div className="p-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shrink-0 shadow-lg shadow-indigo-600/20">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              {!sidebarCollapsed && (
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="font-bold text-sm tracking-tight truncate dark:text-white text-slate-800"
                >
                  AI Advisor
                </motion.span>
              )}
            </div>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg hidden md:block"
            >
              {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>

          {/* Nav Links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3.5 px-3 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all relative ${
                    isActive
                      ? 'text-white bg-indigo-600 shadow-md shadow-indigo-600/20'
                      : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/50'
                  }`}
                  title={item.label}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar bottom */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-2">
          {/* User badge */}
          {user && (
            <div className="flex items-center gap-3 p-2 rounded-xl dark:bg-slate-900 bg-slate-50 border dark:border-slate-850 border-slate-100 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center shrink-0">
                <User className="w-4 h-4" />
              </div>
              {!sidebarCollapsed && (
                <div className="overflow-hidden text-left">
                  <p className="text-xs font-bold truncate dark:text-slate-200 text-slate-700">{user.username}</p>
                  <p className="text-[10px] text-slate-450 dark:text-slate-400 capitalize">{user.role}</p>
                </div>
              )}
            </div>
          )}

          {/* Toggles */}
          <div className="flex flex-col gap-1">
            <button
              onClick={toggleTheme}
              className="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/50 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="w-5 h-5 text-amber-500" />
                  {!sidebarCollapsed && <span>Light Mode</span>}
                </>
              ) : (
                <>
                  <Moon className="w-5 h-5 text-indigo-500" />
                  {!sidebarCollapsed && <span>Dark Mode</span>}
                </>
              )}
            </button>

            <button
              onClick={logout}
              className="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-slate-500 dark:text-slate-400 hover:bg-rose-500/10 hover:text-rose-500 transition-colors"
              title="Logout session"
            >
              <LogOut className="w-5 h-5 shrink-0" />
              {!sidebarCollapsed && <span>Logout</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main content viewport */}
      <main className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Dynamic header wrapper */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.2 }}
              className="max-w-7xl mx-auto h-full"
            >
              {renderView()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

export default App;
