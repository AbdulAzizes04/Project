export default function ChartCard({ title, subtitle, children, className = '' }) {
  return (
    <div className={`forensic-card ${className}`}>
      <div className="mb-4">
        <h3
          style={{
            fontSize: 13, fontWeight: 700, color: '#e2e8f0',
            letterSpacing: '0.04em', marginBottom: 2,
          }}
        >
          {title}
        </h3>
        {subtitle && (
          <p style={{ fontSize: 11, color: '#4a5568' }}>{subtitle}</p>
        )}
      </div>
      {children}
    </div>
  );
}
