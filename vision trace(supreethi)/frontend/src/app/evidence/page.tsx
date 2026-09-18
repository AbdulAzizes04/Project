'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  FastForward,
  Rewind,
  StepForward,
  StepBack,
  Sliders,
  Bookmark,
  Plus,
  Maximize2,
  ZoomIn,
  ZoomOut,
  Layers,
  Sparkles,
  Camera,
  CheckCircle2,
  UserCheck,
  ShieldAlert,
  Footprints,
  EyeOff
} from 'lucide-react';

export default function EvidenceViewerPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [currentFrame, setCurrentFrame] = useState(180);
  const [totalFrames, setTotalFrames] = useState(630);
  const [showBBoxes, setShowBBoxes] = useState(true);
  const [showEnhancementSplit, setShowEnhancementSplit] = useState(false);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const [activeCamera, setActiveCamera] = useState('Camera 04 - Bank Lobby & Vault (Intruder Roaming)');
  const [selectedTrack, setSelectedTrack] = useState<string>('#07');

  // Markers
  const [markers, setMarkers] = useState([
    { frame: 60, time: '11:47:21 PM', type: 'Subject Entry', note: 'Suspect pushes open bank entrance doors and enters lobby', color: '#00e5ff' },
    { frame: 180, time: '11:47:26 PM', type: 'Roaming Activity', note: 'Suspect navigates around queue stanchions towards teller desks', color: '#f59e0b' },
    { frame: 265, time: '11:47:29 PM', type: 'Suspicious Recon', note: 'Subject inspects Teller counter #4 cash drawer and glass partition', color: '#ef4444' },
    { frame: 420, time: '11:47:34 PM', type: 'Vault Loitering', note: 'Subject moves into back corridor, loitering near 24HR ATM & vault door', color: '#ef4444' },
    { frame: 580, time: '11:47:39 PM', type: 'Subject Exit', note: 'Suspect hurries toward glass entrance doors and leaves premises', color: '#10b981' }
  ]);

  const [newMarkerType, setNewMarkerType] = useState('Suspicious Activity');
  const [newMarkerNote, setNewMarkerNote] = useState('');
  const [markerSavedMsg, setMarkerSavedMsg] = useState(false);

  // Sync video time with frames
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
      }
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const duration = videoRef.current.duration || 21;
      const progress = videoRef.current.currentTime / duration;
      setCurrentFrame(Math.round(progress * totalFrames));
    }
  };

  const handleSeek = (frame: number) => {
    setCurrentFrame(frame);
    if (videoRef.current) {
      const duration = videoRef.current.duration || 21;
      videoRef.current.currentTime = (frame / totalFrames) * duration;
    }
  };

  const stepFrame = (delta: number) => {
    const nextF = Math.max(0, Math.min(totalFrames, currentFrame + delta));
    handleSeek(nextF);
  };

  const handleAddMarker = () => {
    const newM = {
      frame: currentFrame,
      time: `11:47:${Math.floor(20 + (currentFrame / totalFrames) * 20)} PM`,
      type: newMarkerType,
      note: newMarkerNote || 'Investigator flagged critical forensic evidence frame',
      color: newMarkerType === 'Suspicious Activity' ? '#ef4444' : '#00e5ff'
    };
    setMarkers([...markers, newM]);
    setNewMarkerNote('');
    setMarkerSavedMsg(true);
    setTimeout(() => setMarkerSavedMsg(false), 2500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#00e5ff] shadow-[0_0_10px_#00e5ff]" />
            <span className="text-xs font-mono font-semibold tracking-widest text-[#00e5ff] uppercase">
              HIGH-PRECISION FORENSIC PLAYER
            </span>
          </div>
          <h1 className="text-2xl font-black font-mono tracking-tight text-white mt-1">
            Bank Surveillance Evidence & Enhancement Console
          </h1>
          <p className="text-xs text-slate-400">
            Playback of Bank Lobby & Vault surveillance feed: One suspect entering, roaming lobby counters and vault, and exiting.
          </p>
        </div>

        {/* Camera Selector Dropdown */}
        <div className="flex items-center space-x-3">
          <select
            value={activeCamera}
            onChange={(e) => setActiveCamera(e.target.value)}
            className="bg-[#07090e] border border-white/15 rounded-xl px-3.5 py-2 text-xs text-white font-mono focus:border-[#00e5ff] focus:outline-none"
          >
            <option value="Camera 04 - Bank Lobby & Vault (Intruder Roaming)">
              Camera 04 - Bank Lobby & Vault (Intruder Roaming)
            </option>
            <option value="Camera 01 - Main Gate Entrance">Camera 01 - Main Gate Entrance</option>
            <option value="Camera 02 - Vault Corridor">Camera 02 - Vault Corridor</option>
            <option value="Camera 03 - West Perimeter">Camera 03 - West Perimeter</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Video Screen & Forensic HUD Controls */}
        <div className="lg:col-span-3 space-y-4">
          <div className="relative aspect-video w-full rounded-2xl overflow-hidden bg-black border border-white/15 shadow-2xl group select-none">
            {!showEnhancementSplit ? (
              <div
                className="relative w-full h-full overflow-hidden flex items-center justify-center bg-black"
                style={{ transform: `scale(${zoomLevel})`, transition: 'transform 0.2s ease-out' }}
              >
                {/* HTML5 Video Element with fallback frame */}
                <video
                  ref={videoRef}
                  src="/videos/bank_suspect_roaming.mp4"
                  className="w-full h-full object-contain"
                  loop
                  playsInline
                  onTimeUpdate={handleTimeUpdate}
                  onEnded={() => setIsPlaying(false)}
                />

                {/* Optional Neural Overlay HUD */}
                {showBBoxes && (
                  <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#00e5ff]/40 text-[11px] font-mono text-[#00e5ff] flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-[#00e5ff] animate-ping" />
                      <span>AI TRAJECTORY & RE-ID ACTIVE (POI #07)</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Low-Light Comparison Slider */
              <div className="relative w-full h-full overflow-hidden select-none">
                <img
                  src="/images/frame_02_suspect_lobby_counters.jpg"
                  alt="Enhanced Frame"
                  className="absolute inset-0 w-full h-full object-cover"
                />
                <div className="absolute top-4 right-4 bg-cyan-950/80 text-[#00e5ff] font-mono text-xs px-3 py-1 rounded-lg border border-[#00e5ff]/40 shadow-lg">
                  CLAHE ENHANCED (LAB + GAMMA 1.45)
                </div>

                <div
                  className="absolute inset-y-0 left-0 overflow-hidden border-r-2 border-[#00e5ff] shadow-[0_0_20px_#00e5ff]"
                  style={{ width: `${sliderPosition}%` }}
                >
                  <img
                    src="/images/frame_04_suspect_vault_loitering.jpg"
                    alt="Raw Low-Light Frame"
                    className="absolute inset-0 w-full h-full object-cover max-w-none"
                    style={{ width: '100%', height: '100%' }}
                  />
                  <div className="absolute top-4 left-4 bg-black/80 text-slate-300 font-mono text-xs px-3 py-1 rounded-lg border border-white/20 shadow-lg">
                    RAW SURVEILLANCE FEED
                  </div>
                </div>

                <input
                  type="range"
                  min="5"
                  max="95"
                  value={sliderPosition}
                  onChange={(e) => setSliderPosition(Number(e.target.value))}
                  className="absolute inset-x-0 bottom-4 mx-auto w-3/4 z-30 opacity-70 hover:opacity-100 cursor-ew-resize accent-[#00e5ff]"
                />
              </div>
            )}

            {/* Live Camera Watermark HUD */}
            <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-xs font-mono text-white flex items-center space-x-3 pointer-events-none">
              <span className="flex items-center space-x-1.5 text-red-400 font-bold">
                <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-red-500 animate-pulse' : 'bg-red-700'}`} />
                <span>{isPlaying ? 'PLAYING' : 'PAUSED'}</span>
              </span>
              <span className="text-slate-400">|</span>
              <span>{activeCamera}</span>
              <span className="text-slate-400">|</span>
              <span className="text-[#00e5ff]">FRAME #{currentFrame} / {totalFrames}</span>
            </div>
          </div>

          {/* Player Controls Bar */}
          <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3">
            {/* Timeline Progress Slider */}
            <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
              <span>11:47:20</span>
              <div className="flex-1 relative">
                <input
                  type="range"
                  min="0"
                  max={totalFrames}
                  value={currentFrame}
                  onChange={(e) => handleSeek(Number(e.target.value))}
                  className="w-full h-2 bg-black/60 rounded-lg appearance-none cursor-pointer accent-[#00e5ff]"
                />
                {/* Evidence Markers Dots */}
                {markers.map((m, i) => (
                  <button
                    key={i}
                    onClick={() => handleSeek(m.frame)}
                    title={`${m.type}: ${m.note}`}
                    className="absolute -top-1 w-2.5 h-2.5 rounded-full ring-2 ring-[#07090e] transition-transform hover:scale-150"
                    style={{ left: `${(m.frame / totalFrames) * 100}%`, backgroundColor: m.color }}
                  />
                ))}
              </div>
              <span>11:47:41</span>
            </div>

            {/* Buttons Row */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => stepFrame(-15)}
                  title="Rewind 15 Frames"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
                >
                  <Rewind className="w-4 h-4" />
                </button>

                <button
                  onClick={() => stepFrame(-1)}
                  title="Step 1 Frame Back"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
                >
                  <StepBack className="w-4 h-4" />
                </button>

                <button
                  onClick={togglePlay}
                  className="p-2.5 rounded-xl bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.4)] transition-all font-bold"
                >
                  {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current" />}
                </button>

                <button
                  onClick={() => stepFrame(1)}
                  title="Step 1 Frame Forward"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
                >
                  <StepForward className="w-4 h-4" />
                </button>

                <button
                  onClick={() => stepFrame(15)}
                  title="Forward 15 Frames"
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
                >
                  <FastForward className="w-4 h-4" />
                </button>
              </div>

              {/* Speeds */}
              <div className="flex items-center space-x-1 font-mono text-xs bg-[#07090e] p-1 rounded-lg border border-white/10">
                {[0.25, 0.5, 1.0, 2.0].map((spd) => (
                  <button
                    key={spd}
                    onClick={() => setPlaybackSpeed(spd)}
                    className={`px-2 py-0.5 rounded text-[11px] transition-all ${
                      playbackSpeed === spd
                        ? 'bg-[#00e5ff]/20 text-[#00e5ff] font-bold'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {spd}x
                  </button>
                ))}
              </div>

              {/* Toggles & Zoom */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowBBoxes(!showBBoxes)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
                    showBBoxes
                      ? 'bg-[#00e5ff]/20 text-[#00e5ff] border border-[#00e5ff]/40 shadow-[0_0_10px_rgba(0,229,255,0.2)]'
                      : 'bg-white/5 text-slate-400 border border-white/10'
                  }`}
                >
                  Overlay {showBBoxes ? 'ON' : 'OFF'}
                </button>

                <button
                  onClick={() => setShowEnhancementSplit(!showEnhancementSplit)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all flex items-center space-x-1.5 ${
                    showEnhancementSplit
                      ? 'bg-purple-600/30 text-purple-300 border border-purple-500/50 shadow-[0_0_12px_rgba(168,85,247,0.3)]'
                      : 'bg-white/5 text-slate-400 border border-white/10'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                  <span>CLAHE Low-Light</span>
                </button>

                <div className="flex items-center space-x-1 border-l border-white/10 pl-2">
                  <button
                    onClick={() => setZoomLevel(prev => Math.max(1.0, prev - 0.25))}
                    className="p-1.5 rounded bg-white/5 text-slate-300 hover:text-white"
                  >
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-[11px] font-mono text-slate-400">{zoomLevel}x</span>
                  <button
                    onClick={() => setZoomLevel(prev => Math.min(2.5, prev + 0.25))}
                    className="p-1.5 rounded bg-white/5 text-slate-300 hover:text-white"
                  >
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Suspect Profile & Evidence Dossier Sidebar */}
        <div className="space-y-4">
          {/* Suspect Identification Dossier Card */}
          <div className="glass-panel rounded-2xl p-4 border border-[#00e5ff]/30 bg-[#07090e]/80 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-[#00e5ff] uppercase flex items-center space-x-1.5">
                <ShieldAlert className="w-4 h-4 text-[#00e5ff]" />
                <span>IDENTIFIED SUSPECT (POI #07)</span>
              </span>
              <span className="text-[10px] font-mono bg-red-500/20 text-red-400 px-2 py-0.5 rounded border border-red-500/40">
                HIGH RELEVANCE (95.2%)
              </span>
            </div>

            {/* Suspect Photo & Silhouette */}
            <div className="grid grid-cols-2 gap-2">
              <div className="relative rounded-xl overflow-hidden border border-white/10 aspect-square group">
                <img
                  src="/images/bank_suspect_portrait.jpg"
                  alt="Suspect Forensic Mugshot"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
                <span className="absolute bottom-1 left-1 text-[9px] font-mono bg-black/80 text-white px-1.5 py-0.5 rounded">
                  CCTV CROP
                </span>
              </div>
              <div className="relative rounded-xl overflow-hidden border border-white/10 aspect-square bg-slate-900 flex items-center justify-center group">
                <img
                  src="/images/bank_suspect_fullbody.jpg"
                  alt="Suspect Full Body"
                  className="w-full h-full object-contain p-1 group-hover:scale-105 transition-transform"
                />
                <span className="absolute bottom-1 left-1 text-[9px] font-mono bg-black/80 text-white px-1.5 py-0.5 rounded">
                  FULL BODY
                </span>
              </div>
            </div>

            {/* Suspect Attributes */}
            <div className="space-y-1.5 font-mono text-[11px]">
              <div className="flex justify-between border-b border-white/5 pb-1">
                <span className="text-slate-400">Biometrics:</span>
                <span className="text-amber-400 flex items-center space-x-1">
                  <EyeOff className="w-3 h-3" />
                  <span>FACE MASKED (98%)</span>
                </span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-1">
                <span className="text-slate-400">Attire:</span>
                <span className="text-slate-200">Navy Hooded Jacket, Cap, Gray Cargo</span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-1">
                <span className="text-slate-400">Gait Profile:</span>
                <span className="text-[#00e5ff] flex items-center space-x-1">
                  <Footprints className="w-3 h-3" />
                  <span>GAIT-007 (92% Cadence)</span>
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Trajectory:</span>
                <span className="text-emerald-400">Entered → Roamed → Exited</span>
              </div>
            </div>
          </div>

          {/* Evidence Annotation Form */}
          <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3">
            <h3 className="font-mono font-bold text-xs text-white flex items-center space-x-2">
              <Bookmark className="w-3.5 h-3.5 text-[#00e5ff]" />
              <span>Flag Forensic Marker</span>
            </h3>

            <div className="space-y-2.5 font-mono text-xs">
              <div>
                <select
                  value={newMarkerType}
                  onChange={(e) => setNewMarkerType(e.target.value)}
                  className="w-full bg-[#07090e] border border-white/15 rounded-lg px-2.5 py-1.5 text-white text-xs focus:border-[#00e5ff] focus:outline-none"
                >
                  <option value="Suspicious Activity">Suspicious Activity</option>
                  <option value="Subject Entry">Subject Entry</option>
                  <option value="Roaming Activity">Roaming Activity</option>
                  <option value="Subject Exit">Subject Exit</option>
                  <option value="Critical Evidence">Critical Evidence</option>
                </select>
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Investigator observation..."
                  value={newMarkerNote}
                  onChange={(e) => setNewMarkerNote(e.target.value)}
                  className="w-full bg-[#07090e] border border-white/15 rounded-lg px-2.5 py-1.5 text-white text-xs font-sans focus:border-[#00e5ff] focus:outline-none"
                />
              </div>

              <button
                onClick={handleAddMarker}
                className="w-full py-1.5 rounded-xl font-bold text-xs bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_12px_rgba(0,229,255,0.3)] transition-all flex items-center justify-center space-x-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>SAVE MARKER</span>
              </button>

              {markerSavedMsg && (
                <div className="p-1.5 rounded bg-emerald-950/40 text-emerald-300 text-[10px] font-sans flex items-center space-x-1.5 border border-emerald-500/30">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  <span>Marker saved at Frame #{currentFrame}.</span>
                </div>
              )}
            </div>
          </div>

          {/* Chronological Event Log */}
          <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
                Bank Incident Timeline
              </span>
              <span className="text-[10px] font-mono text-[#00e5ff] bg-[#00e5ff]/10 px-2 py-0.5 rounded">
                {markers.length} EVENTS
              </span>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {markers.map((m, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSeek(m.frame)}
                  className="p-2.5 rounded-xl bg-[#07090e]/70 border border-white/5 hover:border-white/20 transition-all cursor-pointer space-y-1 group"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="font-bold text-white flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: m.color }} />
                      <span>{m.type}</span>
                    </span>
                    <span className="text-[#00e5ff]">F#{m.frame}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 font-sans line-clamp-2">
                    {m.note}
                  </p>
                  <span className="text-[9px] text-slate-500 font-mono block">
                    {m.time}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
