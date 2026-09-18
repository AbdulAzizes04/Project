import { useState, useEffect, useRef } from 'react';
import { Film, Image, Play, ChevronRight, Settings, Zap, AlertCircle } from 'lucide-react';
import UploadZone from '../components/UploadZone';
import ProcessingPipeline from '../components/ProcessingPipeline';
import Timeline from '../components/Timeline';
import ConfidenceBadge from '../components/ConfidenceBadge';
import {
  createCase, uploadFiles, runAnalysis, getAnalysisStatus,
  getCaseTimeline, getCaseAnalysis, getCaseTracks,
} from '../services/api';

const DEMO_SCENARIOS = [
  { key: 'bank_3min', label: '3-Min Bank CCTV Simulation', icon: '🏦', color: '#00d4ff', desc: '360 frames · 8 tracks · HIGH confidence' },
  { key: 'helmet_demo', label: 'Helmet Removal CCTV Demo', icon: '🪖', color: '#ffc107', desc: '150 frames · 4 tracks · Helmet event' },
  { key: 'bank_standard', label: 'Standard Bank CCTV Demo', icon: '📹', color: '#00ff88', desc: '240 frames · 6 tracks · MEDIUM confidence' },
  { key: 'crowd', label: '4.5-Min Crowd Surveillance', icon: '👥', color: '#7c3aed', desc: '540 frames · 16 tracks · Crowd tracking' },
];

const FPS_OPTIONS = [1, 2, 5, 10];

export default function SearchPipeline() {
  const [videoFile, setVideoFile] = useState(null);
  const [refImage, setRefImage] = useState(null);
  const [threshold, setThreshold] = useState(85);
  const [fps, setFps] = useState(2);
  const [status, setStatus] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [caseId, setCaseId] = useState(null);
  const [results, setResults] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [analysis, setAnalysis] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [error, setError] = useState(null);
  const [activeCaseName, setActiveCaseName] = useState('');
  const pollRef = useRef(null);

  const clearResults = () => {
    setStatus(null); setResults(null); setTimeline([]);
    setAnalysis([]); setTracks([]); setError(null); setCaseId(null);
  };

  const pollStatus = async (id) => {
    try {
      const res = await getAnalysisStatus(id);
      setStatus(res.data);

      if (res.data.status === 'completed') {
        clearInterval(pollRef.current);
        setProcessing(false);
        // Fetch results
        const [tlRes, arRes, trRes] = await Promise.all([
          getCaseTimeline(id),
          getCaseAnalysis(id),
          getCaseTracks(id),
        ]);
        setTimeline(tlRes.data);
        setAnalysis(arRes.data);
        setTracks(trRes.data);
      } else if (res.data.status === 'error') {
        clearInterval(pollRef.current);
        setProcessing(false);
        setError(res.data.message);
      }
    } catch {
      // Backend not reachable; stop polling gracefully
      clearInterval(pollRef.current);
      setProcessing(false);
      setError('Backend connection failed. Please start the FastAPI server.');
    }
  };

  const startDemo = async (scenarioKey) => {
    clearResults();
    setError(null);
    const scenario = DEMO_SCENARIOS.find((s) => s.key === scenarioKey);
    setActiveCaseName(scenario?.label || 'Demo Case');

    try {
      // Create case
      const caseRes = await createCase({ case_name: scenario.label });
      const id = caseRes.data.id;
      setCaseId(id);

      // Start demo pipeline
      await runAnalysis({ case_id: id, demo_mode: true, demo_scenario: scenarioKey, fps: 2, similarity_threshold: 0.85 });
      setProcessing(true);

      pollRef.current = setInterval(() => pollStatus(id), 1200);
    } catch {
      setError('Backend not running. Please start the FastAPI server (uvicorn backend.main:app).');
    }
  };

  const runCustom = async () => {
    if (!videoFile) { setError('Please upload a CCTV video first.'); return; }
    clearResults();
    setError(null);
    setActiveCaseName(`Custom Case — ${videoFile.name}`);

    try {
      const caseRes = await createCase({ case_name: `Custom — ${videoFile.name}` });
      const id = caseRes.data.id;
      setCaseId(id);

      await uploadFiles(id, videoFile, refImage);
      await runAnalysis({ case_id: id, demo_mode: false, fps, similarity_threshold: threshold / 100 });
      setProcessing(true);

      pollRef.current = setInterval(() => pollStatus(id), 1500);
    } catch {
      setError('Upload failed. Ensure the backend server is running.');
    }
  };

  useEffect(() => () => clearInterval(pollRef.current), []);

  const isCompleted = status?.status === 'completed';

  return (
    <div className="p-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="mb-6">
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginBottom: 4 }}>
          Forensic Person Search & Gait Analysis
        </h1>
        <p style={{ fontSize: 13, color: '#4a5568', maxWidth: 640 }}>
          Upload surveillance footage and analyze suspect activity using AI-powered multi-modal forensic intelligence.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* ── Left Panel ──────────────────────────────────────────── */}
        <div className="space-y-4">
          {/* Demo Scenarios */}
          <div className="forensic-card">
            <div className="flex items-center gap-2 mb-4">
              <Zap size={15} color="#00d4ff" />
              <h2 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
                ⚡ 1-Click Demo Scenarios
              </h2>
            </div>
            <div className="space-y-2">
              {DEMO_SCENARIOS.map((sc) => (
                <button
                  key={sc.key}
                  onClick={() => startDemo(sc.key)}
                  disabled={processing}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center', gap: 12,
                    background: '#0f1f3d', border: '1px solid #1a2a4a',
                    borderRadius: 10, padding: '12px 14px', cursor: processing ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s', textAlign: 'left', opacity: processing ? 0.6 : 1,
                  }}
                  onMouseEnter={(e) => !processing && (e.currentTarget.style.borderColor = `${sc.color}55`)}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1a2a4a')}
                >
                  <span style={{ fontSize: 22 }}>{sc.icon}</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: sc.color, marginBottom: 2 }}>
                      {sc.label}
                    </div>
                    <div style={{ fontSize: 11, color: '#4a5568' }}>{sc.desc}</div>
                  </div>
                  <ChevronRight size={14} color="#4a5568" style={{ marginLeft: 'auto' }} />
                </button>
              ))}
            </div>
          </div>

          {/* Analysis Settings */}
          <div className="forensic-card">
            <div className="flex items-center gap-2 mb-4">
              <Settings size={15} color="#00d4ff" />
              <h2 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>Analysis Settings</h2>
            </div>

            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <label style={{ fontSize: 12, color: '#94a3b8', fontWeight: 500 }}>
                  Similarity Threshold
                </label>
                <span style={{ fontSize: 12, color: '#00d4ff', fontWeight: 700 }}>{threshold}%</span>
              </div>
              <input
                type="range" min={50} max={100} value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                style={{ width: '100%' }}
              />
              <div className="flex justify-between mt-1" style={{ fontSize: 10, color: '#4a5568' }}>
                <span>50%</span><span>100%</span>
              </div>
              <p style={{ fontSize: 11, color: '#4a5568', marginTop: 6 }}>
                Minimum confidence required to flag a potential suspect match.
              </p>
            </div>

            <div>
              <label style={{ fontSize: 12, color: '#94a3b8', fontWeight: 500, display: 'block', marginBottom: 8 }}>
                Frame Extraction Frequency
              </label>
              <div className="flex gap-2">
                {FPS_OPTIONS.map((f) => (
                  <button
                    key={f}
                    onClick={() => setFps(f)}
                    style={{
                      flex: 1, padding: '7px 0', borderRadius: 8, fontSize: 12, cursor: 'pointer',
                      fontWeight: 600,
                      background: fps === f ? '#00d4ff22' : '#0f1f3d',
                      border: `1px solid ${fps === f ? '#00d4ff66' : '#1a2a4a'}`,
                      color: fps === f ? '#00d4ff' : '#4a5568',
                      transition: 'all 0.2s',
                    }}
                  >
                    {f} FPS
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── Right Panel ─────────────────────────────────────────── */}
        <div className="space-y-4">
          {/* Upload */}
          <div className="forensic-card">
            <h2 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', marginBottom: 16 }}>
              Custom Case Input
            </h2>
            <div className="space-y-4">
              <div>
                <label style={{ fontSize: 11, color: '#4a5568', display: 'block', marginBottom: 8, letterSpacing: '0.06em', fontWeight: 600 }}>
                  CCTV SURVEILLANCE FOOTAGE
                </label>
                <UploadZone
                  label="Upload CCTV Surveillance Footage"
                  accept=".mp4,.avi,.mov"
                  icon={Film}
                  file={videoFile}
                  onFile={setVideoFile}
                />
              </div>
              <div>
                <label style={{ fontSize: 11, color: '#4a5568', display: 'block', marginBottom: 8, letterSpacing: '0.06em', fontWeight: 600 }}>
                  TARGET REFERENCE PHOTO <span style={{ color: '#1a2a4a' }}>(OPTIONAL)</span>
                </label>
                <UploadZone
                  label="Upload Suspect Reference Image"
                  accept=".jpg,.jpeg,.png"
                  icon={Image}
                  file={refImage}
                  onFile={setRefImage}
                />
              </div>
            </div>
          </div>

          {/* Execute Button */}
          <button
            className="btn-execute"
            onClick={runCustom}
            disabled={processing || !videoFile}
          >
            <Play size={16} style={{ display: 'inline', marginRight: 8 }} />
            EXECUTE SEARCH & GAIT ANALYSIS PIPELINE
          </button>

          {error && (
            <div
              className="animate-fade-in"
              style={{
                background: '#ff444415', border: '1px solid #ff444433',
                borderRadius: 10, padding: '12px 14px',
                display: 'flex', gap: 10, alignItems: 'flex-start',
              }}
            >
              <AlertCircle size={16} color="#ff4444" style={{ flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 12, color: '#ff4444', lineHeight: 1.5 }}>{error}</span>
            </div>
          )}
        </div>
      </div>

      {/* ── Processing Pipeline ──────────────────────────────────── */}
      {(processing || status) && (
        <div className="mt-6">
          <ProcessingPipeline status={status} />
        </div>
      )}

      {/* ── Results ─────────────────────────────────────────────── */}
      {isCompleted && (
        <div className="mt-6 animate-fade-in">
          <div style={{
            fontSize: 14, fontWeight: 700, color: '#00ff88', marginBottom: 16,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            ✓ INVESTIGATION COMPLETE — {activeCaseName}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Tracks */}
            <div className="forensic-card">
              <h3 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', marginBottom: 12 }}>
                Tracked Individuals
              </h3>
              <div className="space-y-2" style={{ maxHeight: 280, overflowY: 'auto' }}>
                {tracks.map((tr) => {
                  const ar = analysis.find((a) => a.track_id === tr.id);
                  return (
                    <div
                      key={tr.id}
                      style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '8px 12px', background: '#0f1f3d', borderRadius: 8,
                        border: '1px solid #1a2a4a',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#00d4ff' }}>
                          Track #{tr.track_number}
                        </div>
                        <div style={{ fontSize: 10, color: '#4a5568' }}>
                          {tr.appearance_count} detections · {tr.duration?.toFixed(1)}s
                        </div>
                      </div>
                      {ar && <ConfidenceBadge rating={ar.evidence_rating} score={ar.final_score} />}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Timeline */}
            <div className="forensic-card">
              <h3 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', marginBottom: 12 }}>
                Evidence Timeline
              </h3>
              <div style={{ maxHeight: 280, overflowY: 'auto' }}>
                <Timeline events={timeline} maxItems={12} />
              </div>
            </div>
          </div>

          {/* Report buttons */}
          <div className="flex gap-3 mt-4">
            <a
              href={`http://localhost:8000/api/reports/${caseId}/pdf`}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}
            >
              📄 Download PDF Report
            </a>
            <a
              href={`http://localhost:8000/api/reports/${caseId}/docx`}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}
            >
              📝 Download DOCX Report
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
