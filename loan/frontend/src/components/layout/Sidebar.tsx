import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, Building2, Network, Atom,
  BarChart3, Shield, History, Database, Lightbulb, Settings,
  Anchor, ChevronLeft, ChevronRight, Ship, AlertTriangle,
} from 'lucide-react';
import { clsx } from '@/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  group?: string;
}

const navItems: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" />, group: 'main' },
  { path: '/prediction', label: 'Loan Prediction', icon: <TrendingUp className="w-4 h-4" />, group: 'main' },
  { path: '/companies', label: 'Companies', icon: <Building2 className="w-4 h-4" />, group: 'main' },
  { path: '/network-analysis', label: 'Network Analysis', icon: <Network className="w-4 h-4" />, group: 'analysis' },
  { path: '/tda-analysis', label: 'TDA Analysis', icon: <Atom className="w-4 h-4" />, group: 'analysis' },
  { path: '/risk-analysis', label: 'Risk Analysis', icon: <AlertTriangle className="w-4 h-4" />, group: 'analysis' },
  { path: '/models', label: 'Models', icon: <BarChart3 className="w-4 h-4" />, group: 'models' },
  { path: '/model-performance', label: 'Performance', icon: <Shield className="w-4 h-4" />, group: 'models' },
  { path: '/explainability', label: 'Explainability', icon: <Lightbulb className="w-4 h-4" />, group: 'models' },
  { path: '/predictions/history', label: 'Pred. History', icon: <History className="w-4 h-4" />, group: 'data' },
  { path: '/data', label: 'Data Management', icon: <Database className="w-4 h-4" />, group: 'data' },
  { path: '/settings', label: 'Settings', icon: <Settings className="w-4 h-4" />, group: 'system' },
];

const groupLabels: Record<string, string> = {
  main: 'Overview',
  analysis: 'Analysis',
  models: 'ML Models',
  data: 'Data',
  system: 'System',
};

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const location = useLocation();

  const groups = ['main', 'analysis', 'models', 'data', 'system'];

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 260 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="h-screen bg-white border-r border-surface-200 flex flex-col fixed left-0 top-0 z-30 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-surface-200 h-16 flex-shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
            <Anchor className="w-4 h-4 text-white" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <p className="text-sm font-bold text-content-primary whitespace-nowrap leading-tight">Maritime Risk</p>
                <p className="text-2xs text-content-tertiary whitespace-nowrap">Intelligence Platform</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-content-tertiary hover:bg-surface-100 hover:text-content-secondary transition-colors flex-shrink-0"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        {groups.map(group => {
          const items = navItems.filter(i => i.group === group);
          if (!items.length) return null;
          return (
            <div key={group} className="mb-4">
              <AnimatePresence>
                {!collapsed && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-2xs font-semibold text-content-tertiary uppercase tracking-wider px-3 mb-1.5"
                  >
                    {groupLabels[group]}
                  </motion.p>
                )}
              </AnimatePresence>
              {items.map(item => {
                const isActive = location.pathname === item.path ||
                  (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    title={collapsed ? item.label : undefined}
                    className={clsx(
                      'sidebar-item group relative',
                      isActive && 'sidebar-item-active',
                      collapsed && 'justify-center px-0'
                    )}
                  >
                    <span className={clsx(
                      'flex-shrink-0',
                      isActive ? 'text-primary-600' : 'text-content-tertiary group-hover:text-content-primary'
                    )}>
                      {item.icon}
                    </span>
                    <AnimatePresence>
                      {!collapsed && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: 'auto' }}
                          exit={{ opacity: 0, width: 0 }}
                          transition={{ duration: 0.15 }}
                          className="overflow-hidden whitespace-nowrap text-sm"
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </NavLink>
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Bottom version info */}
      <div className="p-4 border-t border-surface-200 flex-shrink-0">
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2"
            >
              <Ship className="w-4 h-4 text-content-tertiary flex-shrink-0" />
              <div>
                <p className="text-2xs text-content-tertiary whitespace-nowrap">TDA-ML Platform v1.0</p>
                <p className="text-2xs text-content-tertiary whitespace-nowrap">Final Year Project 2026</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        {collapsed && <Anchor className="w-4 h-4 text-content-tertiary mx-auto" />}
      </div>
    </motion.aside>
  );
};

export default Sidebar;
