import { useState, useEffect } from 'react';
import { Bot, Database } from 'lucide-react';
import ChatInterface from '../components/ChatInterface';
import { listCases } from '../services/api';

export default function ForensicChatbot() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);

  useEffect(() => {
    listCases()
      .then((r) => {
        const completed = r.data.filter((c) => c.status === 'completed');
        setCases(completed);
        if (completed.length) setSelectedCase(completed[0].id);
      })
      .catch(() => {});
  }, []);

  return (
    <div
      className="animate-fade-in"
      style={{ height: 'calc(100vh - 0px)', display: 'flex', flexDirection: 'column', padding: '1.5rem', gap: 16 }}
    >
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginBottom: 4 }}>
            AI Forensic Investigation Assistant
          </h1>
          <p style={{ fontSize: 13, color: '#4a5568' }}>
            Ask questions about investigations — grounded in actual case database
          </p>
        </div>

        {cases.length > 0 && (
          <div className="flex items-center gap-2">
            <Database size={14} color="#4a5568" />
            <select
              value={selectedCase || ''}
              onChange={(e) => setSelectedCase(Number(e.target.value) || null)}
              style={{
                background: '#0f1f3d', border: '1px solid #1a2a4a',
                color: '#94a3b8', borderRadius: 8, padding: '6px 10px',
                fontSize: 12, outline: 'none', cursor: 'pointer',
              }}
            >
              <option value="">All Cases</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  #{c.id} — {c.case_name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* ── Chat + Info ─────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 16, flex: 1, minHeight: 0 }}>
        {/* Chat */}
        <div
          className="forensic-card"
          style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}
        >
          <div
            className="flex items-center gap-3 px-4 py-3"
            style={{ borderBottom: '1px solid #1a2a4a', flexShrink: 0 }}
          >
            <div
              style={{
                width: 32, height: 32, borderRadius: '50%',
                background: '#00d4ff18', border: '1px solid #00d4ff33',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Bot size={16} color="#00d4ff" />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
                VisionTrace AI Agent
              </div>
              <div style={{ fontSize: 11, color: '#4a5568' }}>
                {selectedCase ? `Querying Case #${selectedCase}` : 'All cases context'}
              </div>
            </div>
            <div
              style={{
                marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6,
                fontSize: 11, color: '#00ff88',
              }}
            >
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#00ff88', boxShadow: '0 0 6px #00ff88' }} />
              Online
            </div>
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <ChatInterface caseId={selectedCase} />
          </div>
        </div>

        {/* Info panel */}
        <div className="space-y-3">
          <div className="forensic-card">
            <div style={{ fontSize: 12, fontWeight: 700, color: '#00d4ff', marginBottom: 10, letterSpacing: '0.06em' }}>
              EXAMPLE QUERIES
            </div>
            {[
              'Where did Track 7 first appear?',
              'When was the helmet removed?',
              'How many persons were detected?',
              'Show the evidence timeline',
              'Give me the highest confidence match',
              'Summarize the investigation',
            ].map((q, i) => (
              <div
                key={i}
                style={{
                  padding: '6px 10px', borderRadius: 6, marginBottom: 4,
                  background: '#0f1f3d', border: '1px solid #1a2a4a',
                  fontSize: 11, color: '#94a3b8', fontStyle: 'italic',
                  cursor: 'default',
                }}
              >
                "{q}"
              </div>
            ))}
          </div>

          <div className="forensic-card">
            <div style={{ fontSize: 12, fontWeight: 700, color: '#00d4ff', marginBottom: 10, letterSpacing: '0.06em' }}>
              SYSTEM INFO
            </div>
            <div className="space-y-2" style={{ fontSize: 11, color: '#4a5568' }}>
              <div>🔒 No external LLM API required</div>
              <div>📂 Grounded in SQLite investigation data</div>
              <div>🚫 Cannot invent or hallucinate forensic evidence</div>
              <div>⚡ Real-time DB query engine</div>
            </div>
          </div>

          {cases.length > 0 && (
            <div className="forensic-card">
              <div style={{ fontSize: 12, fontWeight: 700, color: '#00d4ff', marginBottom: 10, letterSpacing: '0.06em' }}>
                AVAILABLE CASES
              </div>
              {cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCase(c.id)}
                  style={{
                    padding: '8px 10px', borderRadius: 6, marginBottom: 4,
                    background: selectedCase === c.id ? '#00d4ff15' : '#0f1f3d',
                    border: `1px solid ${selectedCase === c.id ? '#00d4ff44' : '#1a2a4a'}`,
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 600, color: selectedCase === c.id ? '#00d4ff' : '#e2e8f0' }}>
                    #{c.id} {c.case_name}
                  </div>
                  <div style={{ fontSize: 10, color: '#4a5568' }}>
                    {c.persons_tracked} tracks · {c.evidence_rating}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
