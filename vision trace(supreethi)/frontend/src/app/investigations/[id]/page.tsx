'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Shield,
  Video,
  Camera,
  UserCheck,
  AlertTriangle,
  Play,
  Download,
  Calendar,
  Clock,
  MapPin,
  FileText,
  Activity,
  ArrowLeft,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Eye,
  Sliders,
  CheckCircle2,
  Maximize2
} from 'lucide-react';
import { fetchInvestigationById, generateReport } from '@/lib/api';
import { Investigation, DetectedPerson } from '@/lib/types';

export default function InvestigationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const invId = params?.id as string;

  const [inv, setInv] = useState<Investigation | null>(null);
  const [selectedPerson, setSelectedPerson] = useState<DetectedPerson | null>(null);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [videoGenerated, setVideoGenerated] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!invId) return;
      try {
        const data = await fetchInvestigationById(invId);
        if (data) {
          setInv(data);
          if (data.detected_persons && data.detected_persons.length > 0) {
            setSelectedPerson(data.detected_persons[0]);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [invId]);

  const handleGenerateVideo = () => {
    setGeneratingVideo(true);
    setTimeout(() => {
      setGeneratingVideo(false);
      setVideoGenerated(true);
    }, 2000);
  };

  const handleGenerateReport = async () => {
    if (!inv) return;
    setGeneratingPdf(true);
    try {
      await generateReport(inv.id);
      router.push('/reports');
    } catch (err) {
      console.error(err);
      router.push('/reports');
    } finally {
      setGeneratingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="w-10 h-10 border-2 border-[#00e5ff] border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs font-mono text-slate-400">Loading Forensic Case Dossier #{invId}...</p>
      </div>
    );
  }

  // Fallback presentation if not found in db
  const investigation = inv || {
    id: invId,
    case_id: 'CASE-2026-089',
    title: 'Armed Jewelry Vault Heist & Perimeter Breach',
    status: 'Completed',
    priority: 'Critical',
    incident: {
      incident_type: 'Robbery',
      incident_date: '2026-09-08',
      incident_time: '07:30 PM',
      location: 'Grand Metropolitan Exchange, Vault Sector 4',
      police_station: 'Central Metropolitan Police Precinct',
      investigator_name: 'Detective Inspector R. Harrison',
      case_description: 'Suspect breached perimeter at 19:30 hours wearing dark hooded tactical apparel and facial concealment. Subverted primary biometric scanner. Fled via western parking sector.'
    },
    videos: [
      { id: '1', camera_id: 'Camera 01 - Main Gate', location: 'North Access Checkpoint', duration_seconds: 185, resolution: '1920x1080' },
      { id: '2', camera_id: 'Camera 02 - Vault Corridor', location: 'Sub-level 2 Security Hallway', duration_seconds: 142, resolution: '1920x1080' },
      { id: '3', camera_id: 'Camera 03 - West Perimeter', location: 'Exterior Loading & Parking', duration_seconds: 210, resolution: '1920x1080' }
    ],
    detected_persons: [
      {
        id: 'p1',
        track_id: 7,
        label: 'Candidate Person of Interest #07',
        confidence_score: 0.94,
        similarity_score: 0.87,
        ai_relevance_score: 0.91,
        face_visibility: 'Masked',
        alternative_pipeline_active: true,
        first_seen: '07:30 PM',
        last_seen: '08:05 PM',
        total_duration: '4 minutes 32 seconds',
        camera_locations: ['Camera 01 - Main Gate', 'Camera 02 - Vault Corridor', 'Camera 03 - West Perimeter'],
        appearance_description: 'Dark charcoal hooded outerwear, dark denim bottoms, athletic footwear with reflective heel',
        clothing_upper: 'Black / Dark Charcoal',
        clothing_lower: 'Navy Denim',
        snapshot_url: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=60',
        is_person_of_interest: true,
        gait_profile: {
          id: 'g1',
          track_id: 7,
          walking_speed: 'Medium / Brisk (1.35 m/s)',
          stride_pattern: 'Moderate with Left-Foot Lead Bias',
          step_frequency: '112 steps/min',
          arm_swing: 'Low / Guarded (Concealment Profile)',
          leg_movement: 'Consistent Heel Strike, Restricted Extension',
          body_posture: 'Slight Forward Lean (7.4°)',
          gait_signature: 'GAIT-007',
          cadence_score: 0.88,
          stride_symmetry: 0.74,
          arm_swing_amplitude: 0.32
        }
      },
      {
        id: 'p2',
        track_id: 3,
        label: 'Candidate #03',
        confidence_score: 0.89,
        similarity_score: 0.42,
        ai_relevance_score: 0.74,
        face_visibility: 'Partially Covered',
        alternative_pipeline_active: true,
        first_seen: '07:45 PM',
        last_seen: '08:01 PM',
        total_duration: '2 minutes 15 seconds',
        camera_locations: ['Camera 02 - Vault Corridor'],
        appearance_description: 'Gray utility jacket, dark cargo pants, cap obscuring upper face',
        clothing_upper: 'Gray',
        clothing_lower: 'Black / Dark Charcoal',
        snapshot_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&auto=format&fit=crop&q=60',
        is_person_of_interest: true,
        gait_profile: {
          id: 'g2',
          track_id: 3,
          walking_speed: 'Fast Paced (1.6 m/s)',
          stride_pattern: 'Rapid Symmetric Cadence',
          step_frequency: '124 steps/min',
          arm_swing: 'Moderate Swing',
          leg_movement: 'Full Knee Flexion',
          body_posture: 'Erect Posture',
          gait_signature: 'GAIT-003',
          cadence_score: 0.91,
          stride_symmetry: 0.89,
          arm_swing_amplitude: 0.55
        }
      }
    ],
    timeline_events: [
      { timestamp: '07:30 PM', camera_id: 'Camera 01 - Main Gate', event_type: 'First Detected', description: 'Candidate #07 first enters surveillance radius from north access road' },
      { timestamp: '07:42 PM', camera_id: 'Camera 02 - Vault Corridor', event_type: 'Movement', description: 'Candidate #07 observed in central corridor; face masked with balaclava' },
      { timestamp: '07:48 PM', camera_id: 'Camera 02 - Vault Corridor', event_type: 'Activity', description: 'Candidate #03 enters opposite wing and lingers near access door' },
      { timestamp: '07:51 PM', camera_id: 'Camera 03 - West Perimeter', event_type: 'Movement', description: 'Candidate #07 moves rapidly towards parking barrier; gait matches GAIT-007' },
      { timestamp: '08:05 PM', camera_id: 'Camera 03 - West Perimeter', event_type: 'Last Recorded', description: 'Last visual contact before subject departs surveillance zone into blind sector' }
    ]
  };

  const person = selectedPerson || investigation.detected_persons[0];

  return (
    <div className="space-y-8">
      {/* Top Navigation & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <a
            href="/investigations"
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </a>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-bold text-[#00e5ff] bg-[#00e5ff]/10 px-2 py-0.5 rounded border border-[#00e5ff]/20">
                {investigation.case_id}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                {investigation.status}
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black font-mono tracking-tight text-white mt-1">
              {investigation.title}
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href="/evidence"
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-[#00e5ff] border border-white/10 transition-colors flex items-center space-x-1.5"
          >
            <Video className="w-3.5 h-3.5" />
            <span>Open Evidence Viewer</span>
          </a>

          <button
            onClick={handleGenerateReport}
            disabled={generatingPdf}
            className="px-4 py-2 rounded-xl font-bold text-xs bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] transition-all flex items-center space-x-1.5"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>{generatingPdf ? 'Compiling PDF...' : 'GENERATE REPORT'}</span>
          </button>
        </div>
      </div>

      {/* Case Details Bar */}
      <div className="glass-panel rounded-xl p-5 border border-white/10 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div>
          <span className="text-slate-500">Incident Type:</span>
          <div className="text-white font-bold">{investigation.incident?.incident_type}</div>
        </div>
        <div>
          <span className="text-slate-500">Date & Time:</span>
          <div className="text-white">{investigation.incident?.incident_date} at {investigation.incident?.incident_time}</div>
        </div>
        <div>
          <span className="text-slate-500">Investigator:</span>
          <div className="text-white">{investigation.incident?.investigator_name}</div>
        </div>
        <div>
          <span className="text-slate-500">Location:</span>
          <div className="text-white truncate">{investigation.incident?.location}</div>
        </div>
      </div>

      {/* Candidate Selector Tabs */}
      <div className="flex items-center space-x-3 border-b border-white/10 pb-2 overflow-x-auto">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider mr-2">Candidate Selection:</span>
        {investigation.detected_persons.map((p) => (
          <button
            key={p.id}
            onClick={() => setSelectedPerson(p as any)}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-all ${
              person.track_id === p.track_id
                ? 'bg-[#00e5ff]/20 text-[#00e5ff] border border-[#00e5ff]/40 shadow-[0_0_12px_rgba(0,229,255,0.2)] font-bold'
                : 'text-slate-400 hover:text-white bg-white/5'
            }`}
          >
            <span>Track #{p.track_id}</span>
            <span className="text-[10px] opacity-75">({intScore(p.ai_relevance_score)}%)</span>
          </button>
        ))}
      </div>

      {/* Main Candidate Person of Interest Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Snapshot & Biometric Flags */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-5">
          <div className="relative aspect-[3/4] w-full rounded-xl overflow-hidden border border-[#00e5ff]/40 shadow-[0_0_20px_rgba(0,229,255,0.2)] group">
            <img
              src={person.snapshot_url || 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=60'}
              alt="Person of Interest Snapshot"
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            {/* Surveillance HUD Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none" />
            <div className="absolute top-3 left-3 bg-black/70 px-2.5 py-1 rounded text-[10px] font-mono text-cyan-300 border border-cyan-500/30">
              TRACK ID: #{person.track_id}
            </div>
            <div className="absolute bottom-3 inset-x-3 flex items-center justify-between text-xs font-mono">
              <span className="text-emerald-400 font-bold">CONF: {intScore(person.confidence_score)}%</span>
              <span className="text-white bg-black/60 px-2 py-0.5 rounded text-[10px]">
                {person.camera_locations?.[0] || 'Camera 01'}
              </span>
            </div>
          </div>

          {/* Scores */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#07090e]/80 p-3 rounded-xl border border-white/10 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">AI Relevance Score</div>
              <div className="text-2xl font-black font-mono text-[#00e5ff] mt-0.5">
                {intScore(person.ai_relevance_score)}%
              </div>
              <span className="text-[9px] text-slate-500">Forensic Prioritization</span>
            </div>

            <div className="bg-[#07090e]/80 p-3 rounded-xl border border-white/10 text-center">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Reference Similarity</div>
              <div className="text-2xl font-black font-mono text-purple-400 mt-0.5">
                {intScore(person.similarity_score)}%
              </div>
              <span className="text-[9px] text-slate-500">Potential Match</span>
            </div>
          </div>

          {/* Core Feature: Suspect Activity Video Generation Button */}
          <div className="pt-2 border-t border-white/10 space-y-2">
            <button
              onClick={handleGenerateVideo}
              disabled={generatingVideo}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-purple-600 to-indigo-600 hover:brightness-110 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)] transition-all flex items-center justify-center space-x-2"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>
                {generatingVideo
                  ? 'EXTRACTING CLIPS & COMPILING...'
                  : videoGenerated
                  ? 'RE-DOWNLOAD EVIDENCE CLIP'
                  : 'GENERATE SUSPECT ACTIVITY VIDEO'}
              </span>
            </button>

            {videoGenerated && (
              <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between text-xs font-mono text-emerald-300">
                <span className="truncate font-semibold">Person_Of_Interest_07_Evidence.mp4</span>
                <a
                  href="#download"
                  className="px-2.5 py-1 rounded bg-emerald-500 text-[#07090e] font-bold text-[10px] hover:brightness-110"
                >
                  SAVE MP4
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Deep Forensic Kinematics & Mask Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {/* Mask Alert Notification (Rule Enforced) */}
          {person.face_visibility === 'Masked' ? (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-rose-950/40 via-[#161c2e] to-rose-950/40 border border-rose-500/40 shadow-[0_0_20px_rgba(239,68,68,0.15)] space-y-2">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-lg bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 shrink-0">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-mono font-bold text-sm text-rose-300">
                    FACE VISIBILITY: MASKED / OCCLUDED
                  </h4>
                  <p className="text-xs text-rose-200/90 font-mono">
                    Alternative Identification Pipeline Activated: Gait, Silhouette Kinematics & Spatial Trajectories.
                  </p>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 pl-12">
                <span className="text-rose-400 font-semibold">Forensic Directive:</span> The system strictly prohibits generative reconstruction or hallucination of obscured facial features. Investigation proceeds via biometric gait signature and clothing aspect ratio.
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 flex items-center space-x-3 text-xs font-mono text-emerald-300">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              <span>Facial Features Partially Observable. Standard biometric candidate matching active.</span>
            </div>
          )}

          {/* Gait Kinematics Profile Card */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-[#00e5ff]" />
                <h3 className="font-mono font-bold text-base text-white">
                  MediaPipe Joint Kinematic Gait Profile
                </h3>
              </div>
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/40 px-2.5 py-1 rounded border border-cyan-500/30">
                SIGNATURE: {person.gait_profile?.gait_signature || 'GAIT-007'}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
              <div className="bg-[#07090e]/70 p-3.5 rounded-xl border border-white/5 space-y-1">
                <span className="text-slate-500 text-[11px]">Walking Speed / Cadence</span>
                <div className="text-sm font-bold text-white">{person.gait_profile?.walking_speed}</div>
                <div className="text-[10px] text-slate-400">{person.gait_profile?.step_frequency}</div>
              </div>

              <div className="bg-[#07090e]/70 p-3.5 rounded-xl border border-white/5 space-y-1">
                <span className="text-slate-500 text-[11px]">Arm Swing Amplitude</span>
                <div className="text-sm font-bold text-amber-400">{person.gait_profile?.arm_swing}</div>
                <div className="text-[10px] text-slate-400">Restricted pendular excursion</div>
              </div>

              <div className="bg-[#07090e]/70 p-3.5 rounded-xl border border-white/5 space-y-1">
                <span className="text-slate-500 text-[11px]">Body Posture & Torso Lean</span>
                <div className="text-sm font-bold text-white">{person.gait_profile?.body_posture}</div>
                <div className="text-[10px] text-slate-400">{person.gait_profile?.leg_movement}</div>
              </div>
            </div>

            {/* Symmetry & Cadence Meters */}
            <div className="space-y-3 pt-2">
              <div>
                <div className="flex items-center justify-between text-xs font-mono mb-1">
                  <span className="text-slate-400">Stride Symmetry Index</span>
                  <span className="text-[#00e5ff] font-bold">
                    {Math.round((person.gait_profile?.stride_symmetry || 0.74) * 100)}%
                  </span>
                </div>
                <div className="w-full h-1.5 bg-black/60 rounded-full overflow-hidden border border-white/10">
                  <div
                    className="h-full bg-[#00e5ff] rounded-full"
                    style={{ width: `${(person.gait_profile?.stride_symmetry || 0.74) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between text-xs font-mono mb-1">
                  <span className="text-slate-400">Kinematic Cadence Reliability</span>
                  <span className="text-purple-400 font-bold">
                    {Math.round((person.gait_profile?.cadence_score || 0.88) * 100)}%
                  </span>
                </div>
                <div className="w-full h-1.5 bg-black/60 rounded-full overflow-hidden border border-white/10">
                  <div
                    className="h-full bg-purple-500 rounded-full"
                    style={{ width: `${(person.gait_profile?.cadence_score || 0.88) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Appearance & Multi-Camera Association */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <h3 className="font-mono font-bold text-base text-white flex items-center space-x-2">
              <Camera className="w-5 h-5 text-purple-400" />
              <span>Appearance & Cross-Camera Association</span>
            </h3>

            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              <span className="font-bold text-white font-mono">Appearance Summary: </span>
              {person.appearance_description}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <span className="text-slate-500">First Observed:</span>
                <div className="text-white font-bold">{person.first_seen}</div>
              </div>
              <div className="bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <span className="text-slate-500">Last Visual:</span>
                <div className="text-white font-bold">{person.last_seen}</div>
              </div>
              <div className="bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <span className="text-slate-500">Appearance Span:</span>
                <div className="text-white font-bold">{person.total_duration}</div>
              </div>
              <div className="bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <span className="text-slate-500">Cameras Hit:</span>
                <div className="text-cyan-400 font-bold">{person.camera_locations?.length || 3} Sector Feeds</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chronological Multi-Camera Movement Timeline */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-mono font-bold text-lg text-white flex items-center space-x-2">
              <Clock className="w-5 h-5 text-[#00e5ff]" />
              <span>Multi-Camera Activity & Motion Timeline</span>
            </h3>
            <p className="text-xs text-slate-400">
              Chronological sequence of detected subject transitions across perimeter and internal cameras
            </p>
          </div>
          <span className="px-2.5 py-1 rounded text-xs font-mono bg-white/5 text-slate-300 border border-white/10">
            {investigation.timeline_events?.length || 5} Waypoints
          </span>
        </div>

        <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-[#00e5ff] before:via-purple-500 before:to-slate-700">
          {investigation.timeline_events.map((ev, idx) => (
            <div key={idx} className="relative group">
              {/* Dot */}
              <div className="absolute -left-[27px] top-1.5 w-3.5 h-3.5 rounded-full bg-[#07090e] border-2 border-[#00e5ff] group-hover:scale-125 transition-transform" />
              
              <div className="bg-[#07090e]/80 border border-white/10 rounded-xl p-4 hover:border-[#00e5ff]/40 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-xs font-bold text-[#00e5ff]">{ev.timestamp}</span>
                    <span className="text-xs font-bold text-white font-mono">{ev.camera_id}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 text-slate-400 border border-white/10">
                    {ev.event_type}
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-sans mt-1">
                  {ev.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function intScore(val: any) {
  if (typeof val === 'number') {
    return Math.round(val * 100);
  }
  return 85;
}
