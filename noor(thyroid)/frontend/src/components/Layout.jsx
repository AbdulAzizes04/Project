import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiActivity, FiUsers, FiBarChart2, FiFileText, FiCalendar,
  FiSettings, FiLogOut, FiMenu, FiX, FiChevronRight,
  FiHome, FiPlusCircle, FiDatabase, FiMessageSquare
} from 'react-icons/fi'
import { MdOutlineHealthAndSafety } from 'react-icons/md'
import { useAuthStore, useThemeStore } from '../store/store'
import { adminAPI } from '../services/api'
import DarkModeToggle from './DarkModeToggle'
import NotificationBell from './NotificationBell'

const navItems = [
  { to: '/dashboard',    icon: FiHome,           label: 'Dashboard' },
  { to: '/predict',      icon: FiPlusCircle,      label: 'New Assessment' },
  { to: '/patients',     icon: FiUsers,           label: 'Patients' },
  { to: '/predictions',  icon: FiActivity,        label: 'Predictions' },
  { to: '/appointments', icon: FiCalendar,        label: 'Appointments' },
  { to: '/reports',      icon: FiFileText,        label: 'Reports' },
  { to: '/chat',         icon: FiMessageSquare,   label: 'AI Assistant' },
  { to: '/admin',        icon: FiSettings,        label: 'Admin Panel', adminOnly: true },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { darkMode } = useThemeStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const filteredNav = navItems.filter(item => !item.adminOnly || user?.role === 'admin')

  return (
    <div className={`min-h-screen flex bg-gray-50 ${darkMode ? 'dark bg-gray-950' : ''}`}>
      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-30 lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 240 : 72 }}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className={`
          fixed top-0 left-0 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
          z-40 flex flex-col overflow-hidden shadow-sm
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          transition-transform lg:transition-none
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-gray-100 dark:border-gray-800 min-h-[72px]">
          <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center flex-shrink-0">
            <MdOutlineHealthAndSafety className="text-white text-xl" />
          </div>
          <AnimatePresence>
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
              >
                <p className="font-bold text-primary-700 font-display text-base leading-tight">ThyroAI</p>
                <p className="text-xs text-gray-400">Risk Assessment</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
          {filteredNav.map(({ to, icon: Icon, label }) => {
            const active = location.pathname.startsWith(to)
            return (
              <Link key={to} to={to} onClick={() => setMobileOpen(false)}>
                <div className={`sidebar-link ${active ? 'active' : ''} ${!sidebarOpen ? 'justify-center px-2' : ''}`}>
                  <Icon className="text-lg flex-shrink-0" />
                  <AnimatePresence>
                    {sidebarOpen && (
                      <motion.span
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="truncate"
                      >
                        {label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>
              </Link>
            )
          })}
        </nav>

        {/* User + collapse */}
        <div className="border-t border-gray-100 dark:border-gray-800 px-2 py-3 space-y-1">
          {sidebarOpen && (
            <div className="px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-xl mb-2">
              <p className="text-sm font-semibold text-gray-800 dark:text-white truncate">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-400 truncate capitalize">{user?.role}</p>
            </div>
          )}
          <button onClick={handleLogout} className={`sidebar-link w-full ${!sidebarOpen ? 'justify-center px-2' : ''}`}>
            <FiLogOut className="text-lg flex-shrink-0 text-red-500" />
            {sidebarOpen && <span className="text-red-500">Logout</span>}
          </button>
          <button
            onClick={() => setSidebarOpen(v => !v)}
            className={`sidebar-link w-full hidden lg:flex ${!sidebarOpen ? 'justify-center px-2' : ''}`}
          >
            <motion.div animate={{ rotate: sidebarOpen ? 180 : 0 }}>
              <FiChevronRight className="text-lg" />
            </motion.div>
            {sidebarOpen && <span>Collapse</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main */}
      <div
        className="flex-1 flex flex-col min-h-screen transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? 240 : 72 }}
      >
        {/* Topbar */}
        <header className="sticky top-0 z-20 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 h-[72px] flex items-center px-6 gap-4 shadow-sm">
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden p-2 rounded-xl hover:bg-gray-100"
          >
            <FiMenu className="text-xl" />
          </button>

          <div className="flex-1">
            <h1 className="text-lg font-semibold text-gray-800 dark:text-white font-display">
              {filteredNav.find(n => location.pathname.startsWith(n.to))?.label || 'ThyroAI'}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <NotificationBell />
            <DarkModeToggle />
            <div className="w-9 h-9 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-bold">
              {(user?.full_name || user?.username || 'A')[0].toUpperCase()}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-auto">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}
