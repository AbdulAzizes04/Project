import React from 'react';
import { CheckCircle2, Clock, ArrowRight, UserCheck } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export const StatusTimeline = ({ history = [], currentStatus = 'submitted' }) => {
  if (!history || history.length === 0) {
    return (
      <div className="timeline">
        <div className="timeline-item">
          <div className="timeline-marker" />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <StatusBadge status={currentStatus} />
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Current Status</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Complaint registered into government redressal database.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="timeline">
      {history.map((item, idx) => {
        const isLatest = idx === history.length - 1;
        const toStatus = item.to_status || item.new_status || currentStatus;
        const fromStatus = item.from_status || item.old_status;
        const actorName = item.actor_name || item.changed_by_name;
        const dateStr = item.created_at ? new Date(item.created_at).toLocaleString() : '';

        return (
          <div key={item.id || idx} className="timeline-item">
            <div 
              className="timeline-marker" 
              style={{ background: isLatest ? '#10b981' : toStatus === 'noted' ? '#06b6d4' : '#6366f1' }}
            />
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
              <StatusBadge status={toStatus} />
              {fromStatus && (
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span>from {fromStatus}</span>
                </span>
              )}
              {dateStr && (
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Clock size={12} />
                  {dateStr}
                </span>
              )}
            </div>
            {item.remarks && (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.03)', padding: '0.6rem 0.85rem', borderRadius: 8, border: '1px solid var(--border-subtle)', marginTop: 6, lineHeight: 1.5 }}>
                "{item.remarks}"
              </p>
            )}
            {actorName && (
              <div style={{ fontSize: '0.74rem', color: '#c7d2fe', marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                <UserCheck size={12} color="#818cf8" />
                <span>Updated by {actorName}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
