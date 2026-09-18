import React, { useState, useEffect } from 'react';
import { Bell, Check, ExternalLink } from 'lucide-react';
import api from '../services/api';
import { Link } from 'react-router-dom';

export const NotificationBell = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications');
      if (res.data?.success) {
        setUnreadCount(res.data.unread_count || 0);
        setNotifications(res.data.notifications || []);
      }
    } catch (err) {
      // quiet fail for bell
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error(err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid var(--border-subtle)',
          color: 'var(--text-primary)',
          width: 38,
          height: 38,
          borderRadius: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          position: 'relative',
        }}
        title="Notifications"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: -4,
            right: -4,
            background: '#ef4444',
            color: '#fff',
            fontSize: '0.65rem',
            fontWeight: 700,
            borderRadius: '999px',
            width: 18,
            height: 18,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid var(--bg-main)',
          }}>
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 48,
          right: 0,
          width: 340,
          maxHeight: 420,
          background: 'var(--bg-surface-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 14,
          boxShadow: 'var(--shadow-lg)',
          zIndex: 100,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}>
          <div style={{
            padding: '0.9rem 1.1rem',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Notifications</span>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#818cf8',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                }}
              >
                Mark all read
              </button>
            )}
          </div>

          <div style={{ flex: 1, overflowY: 'auto', maxHeight: 320 }}>
            {notifications.length === 0 ? (
              <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No notifications yet
              </div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  style={{
                    padding: '0.8rem 1.1rem',
                    borderBottom: '1px solid var(--border-subtle)',
                    background: n.is_read ? 'transparent' : 'rgba(99,102,241,0.06)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.3rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: n.is_read ? 'var(--text-secondary)' : '#fff' }}>
                      {n.title}
                    </span>
                    {!n.is_read && (
                      <button
                        onClick={() => markAsRead(n.id)}
                        style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                        title="Mark as read"
                      >
                        <Check size={14} />
                      </button>
                    )}
                  </div>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {n.message}
                  </p>
                  {n.reference_number && (
                    <Link
                      to={`/track?ticket=${n.reference_number}`}
                      onClick={() => setIsOpen(false)}
                      style={{ fontSize: '0.72rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}
                    >
                      <span>Ticket #{n.reference_number}</span>
                      <ExternalLink size={11} />
                    </Link>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
