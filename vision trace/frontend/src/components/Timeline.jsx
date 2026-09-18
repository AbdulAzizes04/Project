const EVENT_COLORS = {
  entry: '#00d4ff',
  exit: '#ff4444',
  helmet_removal: '#ffc107',
  face_visible: '#00ff88',
  high_confidence: '#00ff88',
  gap: '#4a5568',
  reappear: '#00d4ff',
  sustained_presence: '#7c3aed',
  detection: '#00d4ff',
  default: '#4a5568',
};

const EVENT_ICONS = {
  entry: '→',
  exit: '←',
  helmet_removal: '🪖',
  face_visible: '👤',
  high_confidence: '✓',
  gap: '⋯',
  reappear: '↩',
  sustained_presence: '📍',
  detection: '●',
};

export default function Timeline({ events = [], maxItems = 20 }) {
  const displayed = events.slice(0, maxItems);

  if (!displayed.length) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#4a5568', fontSize: 13 }}>
        No timeline events yet. Run an analysis to generate evidence.
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {displayed.map((ev, i) => {
        const color = EVENT_COLORS[ev.event_type] || EVENT_COLORS.default;
        const icon = EVENT_ICONS[ev.event_type] || '●';
        const isLast = i === displayed.length - 1;

        return (
          <div key={ev.id || i} className="flex gap-3 animate-fade-in" style={{ animationDelay: `${i * 0.04}s` }}>
            {/* Timeline spine */}
            <div className="flex flex-col items-center" style={{ paddingTop: 2 }}>
              <div
                style={{
                  width: 28, height: 28, borderRadius: '50%',
                  background: `${color}18`,
                  border: `2px solid ${color}55`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, color, flexShrink: 0,
                }}
              >
                {icon}
              </div>
              {!isLast && (
                <div style={{
                  width: 2, flex: 1, minHeight: 16,
                  background: `linear-gradient(${color}33, #1a2a4a11)`,
                  marginTop: 2,
                }} />
              )}
            </div>

            {/* Content */}
            <div style={{ paddingBottom: isLast ? 0 : 12, paddingTop: 2 }}>
              <div style={{ fontSize: 11, color, fontWeight: 600, fontFamily: 'monospace', marginBottom: 2 }}>
                {ev.timestamp_str || formatTime(ev.timestamp)}
              </div>
              <div style={{ fontSize: 13, color: '#e2e8f0', lineHeight: 1.4 }}>
                {ev.description}
              </div>
              {ev.confidence && (
                <div style={{ fontSize: 10, color: '#4a5568', marginTop: 2 }}>
                  Confidence: {(ev.confidence * 100).toFixed(0)}%
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function formatTime(secs) {
  if (!secs && secs !== 0) return '00:00';
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}
