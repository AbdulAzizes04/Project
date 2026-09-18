import React from 'react';

export const StatsCard = ({ title, value, icon: Icon, color = '#818cf8', subtitle }) => {
  return (
    <div className="glass-card stat-card">
      <div 
        className="stat-icon-wrapper" 
        style={{ 
          background: `${color}18`, 
          borderColor: `${color}35`,
          color: color 
        }}
      >
        {Icon && <Icon size={26} />}
      </div>
      <div>
        <div className="stat-val">{value ?? 0}</div>
        <div className="stat-lbl">{title}</div>
        {subtitle && (
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
