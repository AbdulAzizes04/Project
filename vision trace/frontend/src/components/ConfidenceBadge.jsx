export default function ConfidenceBadge({ rating, score }) {
  const config = {
    HIGH: { cls: 'badge-high', label: 'HIGH' },
    MEDIUM: { cls: 'badge-medium', label: 'MEDIUM' },
    LOW: { cls: 'badge-low', label: 'LOW' },
  };
  const { cls, label } = config[rating] || config.LOW;

  return (
    <span
      className={cls}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '3px 10px', borderRadius: 20,
        fontSize: 11, fontWeight: 700, letterSpacing: '0.06em',
      }}
    >
      <span
        style={{
          width: 6, height: 6, borderRadius: '50%',
          background: 'currentColor',
          boxShadow: '0 0 6px currentColor',
          display: 'inline-block',
        }}
      />
      {label}
      {score !== undefined && (
        <span style={{ opacity: 0.8 }}>({(score * 100).toFixed(1)}%)</span>
      )}
    </span>
  );
}
