export default function StatCard({ title, value, subtitle, icon: Icon, color = '#00d4ff', trend }) {
  const colorMap = {
    cyan: '#00d4ff',
    green: '#00ff88',
    yellow: '#ffc107',
    red: '#ff4444',
  };
  const c = colorMap[color] || color;

  return (
    <div
      className="forensic-card animate-fade-in"
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      {/* Background glow */}
      <div
        style={{
          position: 'absolute', top: -20, right: -20,
          width: 80, height: 80, borderRadius: '50%',
          background: `${c}11`,
          filter: 'blur(20px)',
          pointerEvents: 'none',
        }}
      />

      <div className="flex items-start justify-between mb-3">
        <div
          className="flex items-center justify-center rounded-lg flex-shrink-0"
          style={{
            width: 40, height: 40,
            background: `${c}18`,
            border: `1px solid ${c}33`,
          }}
        >
          {Icon && <Icon size={18} color={c} />}
        </div>
        {trend && (
          <span style={{ fontSize: 11, color: trend > 0 ? '#00ff88' : '#ff4444', fontWeight: 600 }}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>

      <div style={{ fontSize: 28, fontWeight: 800, color: c, lineHeight: 1, marginBottom: 4 }}>
        {value}
      </div>
      <div style={{ fontSize: 13, color: '#94a3b8', fontWeight: 500 }}>{title}</div>
      {subtitle && (
        <div style={{ fontSize: 11, color: '#4a5568', marginTop: 4 }}>{subtitle}</div>
      )}
    </div>
  );
}
