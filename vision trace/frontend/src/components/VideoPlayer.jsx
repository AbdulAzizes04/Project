import { useRef, useState, useEffect } from 'react';
import {
  Play, Pause, Volume2, VolumeX, Maximize2,
  Settings, Eye, EyeOff
} from 'lucide-react';

// Demo bounding boxes for overlay (when no real detections)
const DEMO_DETECTIONS = [
  { track_id: 7, confidence: 0.94, bbox_pct: [0.15, 0.1, 0.42, 0.85], suspect: true },
  { track_id: 3, confidence: 0.82, bbox_pct: [0.55, 0.15, 0.78, 0.88], suspect: false },
];

export default function VideoPlayer({ src, detections = null, caseId }) {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [speed, setSpeed] = useState(1);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showOverlays, setShowOverlays] = useState(true);
  const [showConfidence, setShowConfidence] = useState(true);

  const boxes = detections || DEMO_DETECTIONS;

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    const onTime = () => setProgress(v.currentTime / (v.duration || 1));
    const onDur = () => setDuration(v.duration);
    v.addEventListener('timeupdate', onTime);
    v.addEventListener('loadedmetadata', onDur);
    v.addEventListener('ended', () => setPlaying(false));
    return () => {
      v.removeEventListener('timeupdate', onTime);
      v.removeEventListener('loadedmetadata', onDur);
    };
  }, []);

  const togglePlay = () => {
    const v = videoRef.current;
    if (!v) return;
    if (playing) { v.pause(); } else { v.play(); }
    setPlaying(!playing);
  };

  const seek = (e) => {
    const v = videoRef.current;
    if (!v) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    v.currentTime = pct * v.duration;
  };

  const setSpeedHandler = (s) => {
    setSpeed(s);
    if (videoRef.current) videoRef.current.playbackRate = s;
  };

  const setVolumeHandler = (v) => {
    setVolume(v);
    if (videoRef.current) { videoRef.current.volume = v; videoRef.current.muted = v === 0; }
    setMuted(v === 0);
  };

  const toggleMute = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !muted;
    setMuted(!muted);
  };

  const fullscreen = () => {
    containerRef.current?.requestFullscreen?.();
  };

  const fmt = (s) => {
    const m = Math.floor(s / 60); const sec = Math.floor(s % 60);
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  };

  return (
    <div
      ref={containerRef}
      className="video-container"
      style={{ border: '1px solid #1a2a4a', borderRadius: 12 }}
    >
      {/* ── Video element ───────────────────────────────────────────── */}
      <div style={{ position: 'relative', aspectRatio: '16/9', background: '#000' }}>
        {src ? (
          <video
            ref={videoRef}
            src={src}
            style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
          />
        ) : (
          <div
            style={{
              width: '100%', height: '100%', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: 12, color: '#4a5568',
            }}
          >
            <div style={{ fontSize: 48 }}>📹</div>
            <div style={{ fontSize: 14 }}>No video loaded</div>
            <div style={{ fontSize: 12, color: '#1a2a4a' }}>Upload CCTV footage in the pipeline</div>
          </div>
        )}

        {/* ── AI Overlay bounding boxes ─────────────────────────────── */}
        {showOverlays && (
          <div
            style={{
              position: 'absolute', inset: 0,
              pointerEvents: 'none',
            }}
          >
            {boxes.map((det, i) => {
              const [x1, y1, x2, y2] = det.bbox_pct || [0, 0, 1, 1];
              const borderColor = det.suspect ? '#00ff88' : '#00d4ff';
              return (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    left: `${x1 * 100}%`,
                    top: `${y1 * 100}%`,
                    width: `${(x2 - x1) * 100}%`,
                    height: `${(y2 - y1) * 100}%`,
                    border: `2px solid ${borderColor}`,
                    borderRadius: 4,
                    boxShadow: `0 0 10px ${borderColor}55`,
                  }}
                >
                  {showConfidence && (
                    <div
                      style={{
                        position: 'absolute', top: -22, left: 0,
                        background: `${borderColor}dd`,
                        color: det.suspect ? '#000' : '#000',
                        fontSize: 10, fontWeight: 700,
                        padding: '2px 6px', borderRadius: 3,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {det.suspect ? '⚠ ' : ''}TRACK {det.track_id} | {(det.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* ── Watermark ─────────────────────────────────────────────── */}
        <div
          style={{
            position: 'absolute', top: 10, left: 10,
            fontSize: 10, color: '#00d4ff88', fontFamily: 'monospace',
            fontWeight: 600, letterSpacing: '0.06em',
          }}
        >
          VISIONTRACE AI — LIVE FORENSIC ANALYSIS
        </div>

        {/* ── Click to play ─────────────────────────────────────────── */}
        {src && !playing && (
          <div
            onClick={togglePlay}
            style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', background: 'rgba(0,0,0,0.3)',
            }}
          >
            <div
              style={{
                width: 64, height: 64, borderRadius: '50%',
                background: '#00d4ff22', border: '2px solid #00d4ff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Play size={28} color="#00d4ff" style={{ marginLeft: 4 }} />
            </div>
          </div>
        )}
      </div>

      {/* ── Controls ─────────────────────────────────────────────────── */}
      <div
        style={{
          background: '#0a1628',
          borderTop: '1px solid #1a2a4a',
          padding: '12px 16px',
        }}
      >
        {/* Progress bar */}
        <div
          className="progress-bar mb-3"
          style={{ height: 4, cursor: 'pointer' }}
          onClick={seek}
        >
          <div className="progress-fill" style={{ width: `${progress * 100}%` }} />
        </div>

        <div className="flex items-center justify-between">
          {/* Left controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              style={{
                background: '#00d4ff22', border: '1px solid #00d4ff44',
                borderRadius: 8, width: 36, height: 36,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: '#00d4ff',
              }}
            >
              {playing ? <Pause size={16} /> : <Play size={16} />}
            </button>

            <button onClick={toggleMute} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}>
              {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
            </button>

            <input
              type="range" min={0} max={1} step={0.05} value={muted ? 0 : volume}
              onChange={(e) => setVolumeHandler(Number(e.target.value))}
              style={{ width: 64 }}
            />

            <span style={{ fontSize: 11, color: '#94a3b8', fontFamily: 'monospace' }}>
              {fmt(progress * duration)} / {fmt(duration)}
            </span>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Speed */}
            {[0.5, 1, 1.5, 2].map((s) => (
              <button
                key={s}
                onClick={() => setSpeedHandler(s)}
                style={{
                  padding: '3px 8px', borderRadius: 4, fontSize: 11, cursor: 'pointer',
                  background: speed === s ? '#00d4ff22' : 'transparent',
                  border: `1px solid ${speed === s ? '#00d4ff44' : '#1a2a4a'}`,
                  color: speed === s ? '#00d4ff' : '#4a5568',
                }}
              >
                {s}×
              </button>
            ))}

            <button
              onClick={() => setShowOverlays(!showOverlays)}
              title="Toggle AI overlays"
              style={{
                background: showOverlays ? '#00d4ff22' : 'transparent',
                border: `1px solid ${showOverlays ? '#00d4ff44' : '#1a2a4a'}`,
                color: showOverlays ? '#00d4ff' : '#4a5568',
                borderRadius: 6, padding: '4px 8px', cursor: 'pointer',
              }}
            >
              {showOverlays ? <Eye size={14} /> : <EyeOff size={14} />}
            </button>

            <button
              onClick={fullscreen}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4a5568' }}
            >
              <Maximize2 size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
