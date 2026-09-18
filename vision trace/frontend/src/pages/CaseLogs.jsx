import { useState, useEffect } from 'react';
import { Trash2, Eye, FileText, ExternalLink, RefreshCw, Database, AlertCircle } from 'lucide-react';
import ConfidenceBadge from '../components/ConfidenceBadge';
import { listCases, deleteCase } from '../services/api';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const STATUS_BADGE = {
  completed: { color: '#00ff88', bg: '#00ff8815', label: 'Completed' },
  processing: { color: '#00d4ff', bg: '#00d4ff15', label: 'Processing' },
  pending: { color: '#ffc107', bg: '#ffc10715', label: 'Pending' },
  error: { color: '#ff4444', bg: '#ff444415', label: 'Error' },
};

export default function CaseLogs() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listCases();
      setCases(res.data);
    } catch {
      setError('Could not load cases. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCases(); }, []);

  const handleDelete = async (id) => {
    if (!confirm('Delete this case and all its data?')) return;
    try {
      await deleteCase(id);
      setCases((prev) => prev.filter((c) => c.id !== id));
    } catch {
      alert('Delete failed.');
    }
  };

  const fmtDate = (d) => new Date(d).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div className="p-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginBottom: 4 }}>
            SQLite Case Logs
          </h1>
          <p style={{ fontSize: 13, color: '#4a5568' }}>
            Investigation database — {cases.length} case{cases.length !== 1 ? 's' : ''} stored
          </p>
        </div>
        <button
          onClick={fetchCases}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: '#0f1f3d', border: '1px solid #1a2a4a',
            color: '#94a3b8', borderRadius: 8, padding: '8px 14px',
            cursor: 'pointer', fontSize: 12,
          }}
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Stats summary ───────────────────────────────────────────── */}
      <div
        style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 12, marginBottom: 20,
        }}
      >
        {[
          { label: 'Total Cases', value: cases.length, color: '#00d4ff' },
          { label: 'Completed', value: cases.filter((c) => c.status === 'completed').length, color: '#00ff88' },
          { label: 'Processing', value: cases.filter((c) => c.status === 'processing').length, color: '#ffc107' },
          { label: 'Errors', value: cases.filter((c) => c.status === 'error').length, color: '#ff4444' },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="forensic-card"
            style={{ textAlign: 'center', padding: '12px' }}
          >
            <div style={{ fontSize: 26, fontWeight: 800, color }}>{value}</div>
            <div style={{ fontSize: 11, color: '#4a5568' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* ── Error ───────────────────────────────────────────────────── */}
      {error && (
        <div
          className="mb-4 p-3 rounded-lg flex gap-3 items-center animate-fade-in"
          style={{ background: '#ff444415', border: '1px solid #ff444433' }}
        >
          <AlertCircle size={16} color="#ff4444" />
          <span style={{ fontSize: 12, color: '#ff4444' }}>{error}</span>
        </div>
      )}

      {/* ── Table ───────────────────────────────────────────────────── */}
      <div className="forensic-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#4a5568', fontSize: 14 }}>
            <Database size={32} style={{ margin: '0 auto 8px', opacity: 0.3 }} />
            Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#4a5568', fontSize: 14 }}>
            <Database size={40} style={{ margin: '0 auto 12px', opacity: 0.2 }} />
            <div>No cases found</div>
            <div style={{ fontSize: 12, marginTop: 6 }}>
              Run a demo analysis from the Search & Gait Pipeline
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="forensic-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Case Name</th>
                  <th>Date</th>
                  <th>Video</th>
                  <th>Persons</th>
                  <th>Matches</th>
                  <th>Confidence</th>
                  <th>Rating</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => {
                  const sb = STATUS_BADGE[c.status] || STATUS_BADGE.pending;
                  return (
                    <tr key={c.id} className="animate-fade-in">
                      <td style={{ color: '#00d4ff', fontWeight: 700, fontFamily: 'monospace' }}>
                        #{String(c.id).padStart(4, '0')}
                      </td>
                      <td style={{ color: '#e2e8f0', fontWeight: 500 }}>{c.case_name}</td>
                      <td style={{ fontSize: 11 }}>{fmtDate(c.created_at)}</td>
                      <td style={{ fontSize: 11, maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {c.video_name || '—'}
                      </td>
                      <td style={{ textAlign: 'center' }}>{c.persons_tracked || '—'}</td>
                      <td style={{ textAlign: 'center' }}>{c.matches_found || '—'}</td>
                      <td style={{ textAlign: 'center' }}>
                        {c.overall_confidence ? `${(c.overall_confidence * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td>
                        {c.evidence_rating ? (
                          <ConfidenceBadge rating={c.evidence_rating} />
                        ) : '—'}
                      </td>
                      <td>
                        <span
                          style={{
                            padding: '3px 10px', borderRadius: 20, fontSize: 11,
                            fontWeight: 600, background: sb.bg, color: sb.color,
                            border: `1px solid ${sb.color}33`,
                          }}
                        >
                          {sb.label}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => navigate('/pipeline')}
                            title="Open Investigation"
                            style={{
                              background: '#00d4ff18', border: '1px solid #00d4ff33',
                              color: '#00d4ff', borderRadius: 6, padding: '4px 8px',
                              cursor: 'pointer', fontSize: 11, display: 'flex', alignItems: 'center', gap: 4,
                            }}
                          >
                            <Eye size={12} />
                          </button>
                          <a
                            href={`${API_BASE}/api/reports/${c.id}/pdf`}
                            target="_blank"
                            rel="noreferrer"
                            title="Download PDF"
                            style={{
                              background: '#7c3aed18', border: '1px solid #7c3aed33',
                              color: '#7c3aed', borderRadius: 6, padding: '4px 8px',
                              cursor: 'pointer', fontSize: 11, display: 'flex', alignItems: 'center',
                              textDecoration: 'none',
                            }}
                          >
                            <FileText size={12} />
                          </a>
                          <button
                            onClick={() => handleDelete(c.id)}
                            title="Delete Case"
                            style={{
                              background: '#ff444418', border: '1px solid #ff444433',
                              color: '#ff4444', borderRadius: 6, padding: '4px 8px',
                              cursor: 'pointer', fontSize: 11, display: 'flex', alignItems: 'center',
                            }}
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
