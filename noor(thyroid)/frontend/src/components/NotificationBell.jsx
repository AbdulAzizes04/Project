import React, { useState, useEffect, useRef } from 'react'
import { FiBell, FiCheck } from 'react-icons/fi'
import { motion, AnimatePresence } from 'framer-motion'
import { adminAPI } from '../services/api'
import { formatDistanceToNow } from 'date-fns'

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unread, setUnread] = useState(0)
  const ref = useRef(null)

  const fetch = async () => {
    try {
      const res = await adminAPI.notifications()
      setNotifications(res.data || [])
      setUnread((res.data || []).filter(n => !n.is_read).length)
    } catch {}
  }

  useEffect(() => {
    fetch()
    const i = setInterval(fetch, 30000)
    return () => clearInterval(i)
  }, [])

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const markAllRead = async () => {
    await adminAPI.markAllRead()
    fetch()
  }

  const typeColors = {
    danger:  'bg-red-100 text-red-600',
    warning: 'bg-yellow-100 text-yellow-600',
    success: 'bg-green-100 text-green-600',
    info:    'bg-blue-100 text-blue-600',
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(v => !v)}
        className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors"
      >
        <FiBell className="text-xl text-gray-600" />
        {unread > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center font-bold">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -8 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-12 w-80 bg-white rounded-2xl shadow-glass border border-gray-100 z-50 overflow-hidden"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <span className="font-semibold text-gray-800">Notifications</span>
              {unread > 0 && (
                <button onClick={markAllRead} className="text-xs text-primary-600 hover:underline flex items-center gap-1">
                  <FiCheck /> Mark all read
                </button>
              )}
            </div>
            <div className="max-h-72 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-gray-400 text-sm">No notifications</div>
              ) : (
                notifications.slice(0, 10).map(n => (
                  <div key={n.id} className={`px-4 py-3 border-b border-gray-50 ${!n.is_read ? 'bg-blue-50/50' : ''}`}>
                    <p className="text-sm font-medium text-gray-800">{n.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                    <p className="text-[10px] text-gray-400 mt-1">
                      {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                    </p>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
