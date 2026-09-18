import { useState, useEffect } from 'react';
import {
  Layers, Users, Target, TrendingUp, Clock, Award,
  Activity, RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, BarChart, Bar, AreaChart, Area,
} from 'recharts';
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import Timeline from '../components/Timeline';
import { listCases, getCaseTimeline, getCaseAnalysis } from '../services/api';

// ── Demo data ─────────────────────────────────────────────────────────────────
const DEMO_STATS = {
  total_frames: 150,
  persons_tracked: 16,
  matches_found: 12,
  overall_confidence: 0.944,
  processing_time: 14,
  evidence_rating: 'HIGH',
};

const DEMO_CONFIDENCE_CHART = Array.from({ length: 12 }, (_, i) => ({
  time: `00:${String(i * 5).padStart(2, '0')}`,
  confidence: 75 + Math.sin(i * 0.8) * 12 + i * 1.5,
  threshold: 85,
}));

const DEMO_REID_GAIT_CHART = Array.from({ length: 10 }, (_, i) => ({
  track: `T${i + 1}`,
  reid: 60 + Math.random() * 35,
  gait: 55 + Math.random() * 38,
}));

const DEMO_DETECTION_CHART = Array.from({ length: 14 }, (_, i) => ({
  time: `00:${String(i * 4).padStart(2, '0')}`,
  detections: Math.floor(2 + Math.random() * 6),
}));

const DEMO_TIMELINE = [
  { timestamp: 15, timestamp_str: '00:00:15', event_type: 'entry', description: 'Track 7 entered monitored area', confidence: 0.92 },
  { timestamp: 20, timestamp_str: '00:00:20', event_type: 'detection', description: 'Person detected near entrance', confidence: 0.89 },
  { timestamp: 35, timestamp_str: '00:00:35', event_type: 'helmet_removal', description: 'Helmet removal detected', confidence: 0.87 },
  { timestamp: 45, timestamp_str: '00:00:45', event_type: 'face_visible', description: 'Face visibility improved', confidence: 0.79 },
  { timestamp: 70, timestamp_str: '00:01:10', event_type: 'exit', description: 'Suspect exited camera view', confidence: 0.91 },
];

const CUSTOM_TOOLTIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#0f1f3d', border: '1px solid #1a2a4a',
      borderRadius: 8, padding: '8px 12px', fontSize: 12,
    }}>
      <p style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</strong>
        </p>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(null);
  const [timeline, setTimeline] = useState(DEMO_TIMELINE);
  const [stats, setStats] = useState(DEMO_STATS);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await listCases();
      const allCases = res.data;
      setCases(allCases);
      const completed = allCases.find((c) => c.status === 'completed');
      if (completed) {
        setActiveCase(completed);
        setStats({
          total_frames: completed.total_frames || DEMO_STATS.total_frames,
          persons_tracked: completed.persons_tracked || DEMO_STATS.persons_tracked,
          matches_found: completed.matches_found || DEMO_STATS.matches_found,
          overall_confidence: completed.overall_confidence || DEMO_STATS.overall_confidence,
          processing_time: completed.processing_time || DEMO_STATS.processing_time,
          evidence_rating: completed.evidence_rating || DEMO_STATS.evidence_rating,
        });
        const tlRes = await getCaseTimeline(completed.id);
        if (tlRes.data?.length) setTimeline(tlRes.data);
      }
    } catch {
      // Use demo data on API failure
    } finally {
      setLoading(false);
    }
  };

  const ratingColor = { HIGH: '#00ff88', MEDIUM: '#ffc107', LOW: '#ff4444' };

  return (
    <div className="p-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', marginBottom: 4 }}>
            VisionTrace AI Dashboard
          </h1>
          <p style={{ fontSize: 13, color: '#4a5568' }}>
            AI-Powered Forensic Surveillance Intelligence
            {!activeCase && (
              <span
                style={{
                  marginLeft: 10, padding: '2px 8px', borderRadius: 10,
                  background: '#ffc10722', border: '1px solid #ffc10744',
                  color: '#ffc107', fontSize: 11, fontWeight: 600,
                }}
              >
                DEMO / SIMULATED DATA
              </span>
            )}
          </p>
        </div>
        <button
          onClick={fetchData}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: '#0f1f3d', border: '1px solid #1a2a4a',
            color: '#94a3b8', borderRadius: 8, padding: '8px 14px',
            cursor: 'pointer', fontSize: 12,
          }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Stat Cards ─────────────────────────────────────────────────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 16, marginBottom: 24,
        }}
      >
        <StatCard
          title="Frames Processed"
          value={stats.total_frames.toLocaleString()}
          subtitle="Total frames analyzed"
          icon={Layers}
          color="cyan"
        />
        <StatCard
          title="Unique Tracks"
          value={stats.persons_tracked}
          subtitle="Persons tracked"
          icon={Users}
          color="cyan"
        />
        <StatCard
          title="Potential Matches"
          value={stats.matches_found}
          subtitle="Suspect detections"
          icon={Target}
          color="green"
        />
        <StatCard
          title="Evidence Confidence"
          value={`${(stats.overall_confidence * 100).toFixed(1)}%`}
          subtitle="Overall accuracy"
          icon={TrendingUp}
          color="green"
        />
        <StatCard
          title="Analysis Duration"
          value={`${stats.processing_time}s`}
          subtitle="Processing time"
          icon={Clock}
          color="yellow"
        />
        <StatCard
          title="Evidence Rating"
          value={stats.evidence_rating}
          subtitle="Classification"
          icon={Award}
          color={stats.evidence_rating === 'HIGH' ? 'green' : stats.evidence_rating === 'MEDIUM' ? 'yellow' : 'red'}
        />
      </div>

      {/* ── Charts Row 1 ───────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <ChartCard title="Multi-Modal Target Confidence Over Time" subtitle="Confidence % across video duration">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={DEMO_CONFIDENCE_CHART}>
              <defs>
                <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2a4a" />
              <XAxis dataKey="time" tick={{ fill: '#4a5568', fontSize: 10 }} />
              <YAxis domain={[60, 100]} tick={{ fill: '#4a5568', fontSize: 10 }} />
              <Tooltip content={<CUSTOM_TOOLTIP />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Area type="monotone" dataKey="confidence" stroke="#00d4ff" fill="url(#confGrad)" strokeWidth={2} name="Confidence %" />
              <Line type="monotone" dataKey="threshold" stroke="#ffc107" strokeDasharray="5 5" strokeWidth={1} name="Threshold" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Re-ID vs Gait Analysis" subtitle="Score comparison per tracked individual">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={DEMO_REID_GAIT_CHART}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2a4a" />
              <XAxis dataKey="track" tick={{ fill: '#4a5568', fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#4a5568', fontSize: 10 }} />
              <Tooltip content={<CUSTOM_TOOLTIP />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="reid" fill="#00d4ff" name="Person Re-ID" radius={[3, 3, 0, 0]} />
              <Bar dataKey="gait" fill="#00ff8877" name="Gait Score" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* ── Charts Row 2 + Timeline ─────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 16 }}>
        <ChartCard title="Detection Activity Timeline" subtitle="Number of detections per timestamp">
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={DEMO_DETECTION_CHART}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2a4a" />
              <XAxis dataKey="time" tick={{ fill: '#4a5568', fontSize: 9 }} />
              <YAxis tick={{ fill: '#4a5568', fontSize: 10 }} />
              <Tooltip content={<CUSTOM_TOOLTIP />} />
              <Bar dataKey="detections" fill="#7c3aed" name="Detections" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="forensic-card">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} color="#00d4ff" />
            <h3 style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
              Recent Investigation Activity
            </h3>
          </div>
          <Timeline events={timeline} maxItems={8} />
        </div>
      </div>
    </div>
  );
}
