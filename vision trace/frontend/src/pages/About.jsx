import { Shield } from 'lucide-react';

const TECH_STACK = [
  { name: 'React 18', desc: 'Frontend framework', emoji: '⚛️', color: '#00d4ff' },
  { name: 'FastAPI', desc: 'Python backend API', emoji: '⚡', color: '#00ff88' },
  { name: 'Python 3.11', desc: 'Core language', emoji: '🐍', color: '#ffc107' },
  { name: 'YOLOv8', desc: 'Person detection', emoji: '👁️', color: '#00d4ff' },
  { name: 'PyTorch', desc: 'Deep learning', emoji: '🔥', color: '#ff6b35' },
  { name: 'OpenCV', desc: 'Computer vision', emoji: '📷', color: '#00ff88' },
  { name: 'ByteTrack', desc: 'Multi-object tracking', emoji: '🎯', color: '#7c3aed' },
  { name: 'SQLite', desc: 'Case database', emoji: '🗄️', color: '#ffc107' },
  { name: 'ReportLab', desc: 'PDF generation', emoji: '📄', color: '#ff4444' },
  { name: 'Recharts', desc: 'Analytics charts', emoji: '📊', color: '#00d4ff' },
  { name: 'Vite', desc: 'Build tool', emoji: '⚡', color: '#ffc107' },
  { name: 'Tailwind CSS', desc: 'Styling', emoji: '🎨', color: '#7c3aed' },
];

const PIPELINE_STEPS = [
  'CCTV Video Input',
  'Frame Extraction (OpenCV)',
  'YOLOv8 Person Detection',
  'ByteTrack Multi-Object Tracking',
  'Person Re-Identification',
  'Gait Analysis',
  'Multi-Modal Score Fusion',
  'Evidence Timeline Generation',
  'SQLite Case Storage',
  'AI Forensic Chatbot',
  'PDF / DOCX Report',
];

export default function About() {
  return (
    <div className="p-6 animate-fade-in" style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* ── Hero ────────────────────────────────────────────────────── */}
      <div
        className="forensic-card mb-6"
        style={{
          background: 'linear-gradient(135deg, #050b18 0%, #0f1f3d 100%)',
          border: '1px solid #00d4ff33',
          textAlign: 'center',
          padding: '3rem 2rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute', inset: 0,
            background: 'radial-gradient(circle at 50% 50%, #00d4ff08 0%, transparent 70%)',
            pointerEvents: 'none',
          }}
        />
        <div
          className="flex items-center justify-center mx-auto mb-4"
          style={{
            width: 64, height: 64, borderRadius: 16,
            background: 'linear-gradient(135deg, #00d4ff22, #0066ff33)',
            border: '1px solid #00d4ff44',
          }}
        >
          <Shield size={30} color="#00d4ff" />
        </div>
        <h1
          style={{
            fontSize: 32, fontWeight: 900, letterSpacing: '0.05em',
            color: '#00d4ff', marginBottom: 8,
          }}
        >
          VisionTrace AI
        </h1>
        <p style={{ fontSize: 15, color: '#94a3b8', maxWidth: 600, margin: '0 auto 16px' }}>
          An Intelligent Forensic Surveillance Platform for Smart Crime Investigation and Rapid Evidence Analysis
        </p>
        <div
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 16px', borderRadius: 20,
            background: '#00ff8815', border: '1px solid #00ff8833',
            fontSize: 12, color: '#00ff88', fontWeight: 600,
          }}
        >
          🎓 B.Tech AI & Data Science — Final Year Project
        </div>
      </div>

      {/* ── Description ─────────────────────────────────────────────── */}
      <div
        className="forensic-card mb-6"
        style={{ borderLeft: '3px solid #00d4ff' }}
      >
        <h2 style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0', marginBottom: 12 }}>
          Project Overview
        </h2>
        <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.8, marginBottom: 12 }}>
          VisionTrace AI is an AI-powered forensic surveillance platform designed to assist investigators
          in analyzing CCTV footage, tracking individuals across video frames, identifying potential suspects
          through multi-modal biometric comparison, and generating professional investigation reports.
        </p>
        <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.8 }}>
          The system combines <strong style={{ color: '#00d4ff' }}>YOLOv8 person detection</strong>,{' '}
          <strong style={{ color: '#00d4ff' }}>ByteTrack multi-object tracking</strong>,{' '}
          <strong style={{ color: '#00d4ff' }}>person re-identification</strong> via appearance embeddings,
          and a prototype <strong style={{ color: '#00d4ff' }}>gait analysis module</strong> into a unified
          forensic intelligence pipeline.
        </p>
        <div
          className="mt-3 p-3 rounded-lg"
          style={{ background: '#ffc10715', border: '1px solid #ffc10733', fontSize: 11, color: '#ffc107' }}
        >
          ⚠️ DISCLAIMER: This is an academic prototype. AI confidence scores are computational estimates
          and are NOT legally conclusive. Results must be reviewed by qualified forensic professionals.
        </div>
      </div>

      {/* ── AI Pipeline ─────────────────────────────────────────────── */}
      <div className="forensic-card mb-6">
        <h2 style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0', marginBottom: 16 }}>
          AI Processing Pipeline
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step} className="flex items-center gap-3">
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: '#00d4ff18', border: '2px solid #00d4ff44',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10, fontWeight: 700, color: '#00d4ff', flexShrink: 0,
                  }}
                >
                  {i + 1}
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div style={{ width: 2, height: 16, background: '#1a2a4a' }} />
                )}
              </div>
              <div style={{ paddingBottom: i < PIPELINE_STEPS.length - 1 ? 16 : 0, paddingTop: 4 }}>
                <span style={{ fontSize: 13, color: '#e2e8f0', fontWeight: 500 }}>{step}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Tech Stack ──────────────────────────────────────────────── */}
      <div className="forensic-card mb-6">
        <h2 style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0', marginBottom: 16 }}>
          Technology Stack
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
            gap: 12,
          }}
        >
          {TECH_STACK.map((tech) => (
            <div
              key={tech.name}
              className="flex items-center gap-3 p-3 rounded-lg"
              style={{
                background: '#0f1f3d',
                border: `1px solid ${tech.color}22`,
                transition: 'border-color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = `${tech.color}55`)}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = `${tech.color}22`)}
            >
              <span style={{ fontSize: 22 }}>{tech.emoji}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: tech.color }}>{tech.name}</div>
                <div style={{ fontSize: 10, color: '#4a5568' }}>{tech.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Features ────────────────────────────────────────────────── */}
      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}
      >
        {[
          {
            title: 'AI Detection & Tracking',
            items: ['YOLOv8 person detection', 'ByteTrack multi-object tracking', 'Persistent track IDs', 'Multi-frame consistency'],
          },
          {
            title: 'Forensic Intelligence',
            items: ['Person re-identification', 'Gait pattern analysis', 'Multi-modal score fusion', 'Evidence timeline generation'],
          },
          {
            title: 'Case Management',
            items: ['SQLite case database', 'Investigation logs', 'Chronological evidence', 'Case deletion & archival'],
          },
          {
            title: 'Reports & Analysis',
            items: ['AI forensic chatbot', 'PDF report generation', 'DOCX report export', 'Dashboard analytics'],
          },
        ].map((sec) => (
          <div key={sec.title} className="forensic-card">
            <h3 style={{ fontSize: 13, fontWeight: 700, color: '#00d4ff', marginBottom: 10 }}>{sec.title}</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {sec.items.map((item) => (
                <li key={item} style={{ fontSize: 12, color: '#94a3b8', marginBottom: 6, display: 'flex', gap: 8 }}>
                  <span style={{ color: '#00ff88' }}>✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div style={{ textAlign: 'center', padding: '1rem', fontSize: 11, color: '#1a2a4a' }}>
        VisionTrace AI · B.Tech Final Year Project · AI & Data Science · Built with ❤️
      </div>
    </div>
  );
}
