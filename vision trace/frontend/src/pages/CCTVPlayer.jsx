import { useState, useEffect } from 'react';
import { Video, ToggleLeft, ToggleRight } from 'lucide-react';
import VideoPlayer from '../components/VideoPlayer';
import { listCases } from '../services/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function CCTVPlayer() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  useEffect(() => {
    listCases()
      .then((r) => {
        const completed = r.data.filter((c) => c.status === 'completed' && c.video_name);
        setCases(completed);
        if (completed.length) setSelectedCase(completed[0]);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedCase?.video_name) {
      setVideoUrl(`${API_BASE}/uploads/videos/${selectedCase.video_name}`);
    } else {
      setVideoUrl(null);
    }
  }, [selectedCase]);

  return (
    <div className="p-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginBottom: 4 }}>
            CCTV Video Player
          </h1>
          <p style={{ fontSize: 13, color: '#4a5568' }}>
            Review surveillance footage with AI-powered detection overlays
          </p>
        </div>

        {cases.length > 0 && (
          <select
            value={selectedCase?.id || ''}
            onChange={(e) => setSelectedCase(cases.find((c) => c.id === Number(e.target.value)))}
            style={{
              background: '#0f1f3d', border: '1px solid #1a2a4a',
              color: '#94a3b8', borderRadius: 8, padding: '8px 12px',
              fontSize: 12, outline: 'none',
            }}
          >
            {cases.map((c) => (
              <option key={c.id} value={c.id}>#{c.id} — {c.case_name}</option>
            ))}
          </select>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 20 }}>
        {/* ── Video Player ─────────────────────────────────────────── */}
        <div>
          <VideoPlayer src={videoUrl} caseId={selectedCase?.id} />

          {/* Overlay Legend */}
          <div
            className="flex items-center gap-4 mt-3 p-3 rounded-lg"
            style={{ background: '#0f1f3d', border: '1px solid #1a2a4a' }}
          >
            <div style={{ fontSize: 11, color: '#4a5568', fontWeight: 600, letterSpacing: '0.06em' }}>AI OVERLAYS:</div>
            <div className="flex items-center gap-2">
              <div style={{ width: 20, height: 2, background: '#00ff88' }} />
              <span style={{ fontSize: 11, color: '#94a3b8' }}>Suspect Match</span>
            </div>
            <div className="flex items-center gap-2">
              <div style={{ width: 20, height: 2, background: '#00d4ff' }} />
              <span style={{ fontSize: 11, color: '#94a3b8' }}>Tracked Person</span>
            </div>
          </div>
        </div>

        {/* ── Info Panel ──────────────────────────────────────────── */}
        <div className="space-y-3">
          {selectedCase ? (
            <>
              <div className="forensic-card">
                <div style={{ fontSize: 11, color: '#00d4ff', fontWeight: 700, letterSpacing: '0.06em', marginBottom: 10 }}>
                  ACTIVE CASE
                </div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>
                  {selectedCase.case_name}
                </div>
                <div style={{ fontSize: 11, color: '#4a5568', marginBottom: 10 }}>
                  Case #{selectedCase.id}
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Persons Tracked', value: selectedCase.persons_tracked },
                    { label: 'Matches Found', value: selectedCase.matches_found },
                    { label: 'Confidence', value: `${(selectedCase.overall_confidence * 100).toFixed(1)}%` },
                    { label: 'Evidence Rating', value: selectedCase.evidence_rating },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex justify-between" style={{ fontSize: 12 }}>
                      <span style={{ color: '#4a5568' }}>{label}</span>
                      <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="forensic-card">
                <div style={{ fontSize: 11, color: '#00d4ff', fontWeight: 700, letterSpacing: '0.06em', marginBottom: 10 }}>
                  DETECTION INFO
                </div>
                <div style={{ fontSize: 11, color: '#4a5568', lineHeight: 1.6 }}>
                  Bounding boxes show tracked individuals.<br />
                  Green boxes indicate suspect matches.<br />
                  Cyan boxes are other tracked persons.
                </div>
              </div>
            </>
          ) : (
            <div className="forensic-card" style={{ textAlign: 'center', color: '#4a5568' }}>
              <Video size={32} style={{ margin: '0 auto 8px' }} />
              <div style={{ fontSize: 13 }}>No completed investigations</div>
              <div style={{ fontSize: 11, marginTop: 4 }}>
                Run a demo analysis from the Pipeline page
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
