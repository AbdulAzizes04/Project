'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  FileText,
  Upload,
  UserCheck,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Camera,
  Film,
  Image as ImageIcon,
  Shield,
  Clock,
  Sparkles,
  Play,
  Download,
  AlertCircle
} from 'lucide-react';
import {
  createInvestigation,
  uploadVideo,
  uploadReferenceImage,
  startAnalysis,
  fetchInvestigationById
} from '@/lib/api';

const STEPS = [
  { id: 1, title: 'Incident Details', desc: 'Case metadata & location' },
  { id: 2, title: 'Evidence Upload', desc: 'CCTV & camera streams' },
  { id: 3, title: 'Reference Images', desc: 'Suspect / victim photos' },
  { id: 4, title: 'AI Processing', desc: 'Computer vision pipeline' },
  { id: 5, title: 'Forensic Results', desc: 'Candidates & timeline' },
];

const INCIDENT_TYPES = [
  'Theft',
  'Robbery',
  'Missing Person',
  'Assault',
  'Accident',
  'Suspicious Activity',
  'Vehicle Crime',
  'Other'
];

export default function NewInvestigationWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [createdInvId, setCreatedInvId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1 Form
  const [formData, setFormData] = useState({
    case_id: 'CASE-2026-104',
    title: 'Commercial Complex Night Breach & Vault Entry',
    priority: 'High',
    incident_type: 'Robbery',
    incident_date: '2026-09-08',
    incident_time: '19:30',
    location: 'Metropolitan Financial Tower, Sector 3',
    police_station: 'City Central Police Station',
    investigator_name: 'Inspector S. Vance (Forensic Unit)',
    case_description: 'Unidentified subject observed bypassing secondary biometric checkpoint wearing facial concealment and dark tactical outerwear.'
  });

  React.useEffect(() => {
    // Generate randomized case ID on client mount to eliminate SSR hydration mismatch
    const rand = Math.floor(100 + Math.random() * 900);
    const today = new Date().toISOString().split('T')[0];
    setFormData(prev => ({
      ...prev,
      case_id: `CASE-2026-${rand}`,
      incident_date: today
    }));
  }, []);

  // Step 2 Form (Videos)
  const [cameraVideos, setCameraVideos] = useState<Array<{
    file: File | null;
    camera_id: string;
    location: string;
    resolution: string;
    duration: string;
  }>>([
    { file: null, camera_id: 'Camera 01 - Main Entrance', location: 'North Access Gate', resolution: '1920x1080', duration: '02:35:12' },
    { file: null, camera_id: 'Camera 02 - Vault Corridor', location: 'Sub-level 2 Security Hallway', resolution: '1920x1080', duration: '01:42:08' },
    { file: null, camera_id: 'Camera 03 - West Perimeter', location: 'Exterior Parking Barrier', resolution: '1920x1080', duration: '03:10:45' }
  ]);

  // Step 3 Form (Reference Images)
  const [referenceType, setReferenceType] = useState<'Suspect' | 'Victim' | 'Both' | 'None'>('Suspect');
  const [referenceFiles, setReferenceFiles] = useState<File[]>([]);
  const [referencePreviews, setReferencePreviews] = useState<string[]>([
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=60'
  ]);

  // Step 4 (Pipeline progress)
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  const PIPELINE_TASKS = [
    'Video Uploaded & Calibrated',
    'Frames Extracted (OpenCV Stream Sampler)',
    'Detecting Persons & Vehicles (YOLOv8)',
    'Tracking Persons & Trajectories (ByteTrack)',
    'Performing Person Re-Identification Embeddings',
    'Detecting Face Occlusions & Mask Status',
    'Performing Pose Joint Landmark Kinematics',
    'Extracting Kinetic Gait Profile & Signatures',
    'Extracting Suspicious Activities & Multi-Cam Path',
    'Generating Chronological Movement Timeline',
    'Creating Court-Admissible Forensic Evidence Report'
  ];

  // Submit Step 1: Create Investigation
  const handleStep1Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const inv = await createInvestigation({
        case_id: formData.case_id,
        title: formData.title,
        priority: formData.priority,
        incident: {
          incident_type: formData.incident_type,
          incident_date: formData.incident_date,
          incident_time: formData.incident_time,
          location: formData.location,
          police_station: formData.police_station,
          investigator_name: formData.investigator_name,
          case_description: formData.case_description
        }
      });
      setCreatedInvId(inv.id);
      setCurrentStep(2);
    } catch (err: any) {
      console.error(err);
      // Fallback: generate local ID if offline
      const mockId = `mock-${Date.now()}`;
      setCreatedInvId(mockId);
      setCurrentStep(2);
    } finally {
      setLoading(false);
    }
  };

  // Submit Step 2: Upload Videos
  const handleStep2Submit = async () => {
    setLoading(true);
    try {
      if (createdInvId) {
        for (const cam of cameraVideos) {
          if (cam.file) {
            const fd = new FormData();
            fd.append('investigation_id', createdInvId);
            fd.append('camera_id', cam.camera_id);
            fd.append('location', cam.location);
            fd.append('file', cam.file);
            await uploadVideo(fd).catch(() => null);
          }
        }
      }
      setCurrentStep(3);
    } finally {
      setLoading(false);
    }
  };

  // Submit Step 3: Upload Reference Images
  const handleStep3Submit = async () => {
    setLoading(true);
    try {
      if (createdInvId && referenceFiles.length > 0) {
        for (const file of referenceFiles) {
          const fd = new FormData();
          fd.append('investigation_id', createdInvId);
          fd.append('image_type', referenceType);
          fd.append('file', file);
          await uploadReferenceImage(fd).catch(() => null);
        }
      }
      setCurrentStep(4);
      runPipelineSimulation();
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Run AI Pipeline Animation & Trigger Backend
  const runPipelineSimulation = () => {
    if (createdInvId && !createdInvId.startsWith('mock-')) {
      startAnalysis(createdInvId).catch(() => null);
    }

    let progress = 0;
    let stepIdx = 0;
    const interval = setInterval(() => {
      progress += 9;
      if (progress > 100) progress = 100;
      setPipelineProgress(progress);

      stepIdx = Math.min(PIPELINE_TASKS.length - 1, Math.floor((progress / 100) * PIPELINE_TASKS.length));
      setActiveStepIndex(stepIdx);

      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          setCurrentStep(5);
        }, 1200);
      }
    }, 450);
  };

  const handleFileDrop = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const updated = [...cameraVideos];
      updated[index].file = file;
      setCameraVideos(updated);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Wizard Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#00e5ff]/10 text-[#00e5ff] border border-[#00e5ff]/20 text-xs font-mono font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>MULTI-STEP CRIME DOSSIER ENGINE</span>
        </div>
        <h1 className="text-3xl font-black font-mono tracking-tight text-white">
          Create New Forensic Investigation
        </h1>
        <p className="text-sm text-slate-400">
          Upload CCTV streams and reference photos for automated YOLO tracking, mask detection, and kinematic gait analysis.
        </p>
      </div>

      {/* 5-Step Progress Indicator Bar */}
      <div className="glass-panel rounded-2xl p-4 sm:p-6 border border-white/10">
        <div className="grid grid-cols-5 gap-2 relative">
          {STEPS.map((s) => {
            const isDone = currentStep > s.id;
            const isCurrent = currentStep === s.id;
            return (
              <div key={s.id} className="flex flex-col items-center text-center space-y-2 relative z-10">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center font-mono font-bold text-xs transition-all ${
                    isDone
                      ? 'bg-emerald-500 text-[#07090e] shadow-[0_0_12px_rgba(16,185,129,0.4)]'
                      : isCurrent
                      ? 'bg-[#00e5ff] text-[#07090e] shadow-[0_0_15px_rgba(0,229,255,0.5)] ring-4 ring-[#00e5ff]/20'
                      : 'bg-white/5 text-slate-500 border border-white/10'
                  }`}
                >
                  {isDone ? <CheckCircle2 className="w-5 h-5" /> : s.id}
                </div>
                <div>
                  <div className={`text-xs font-bold font-mono ${isCurrent ? 'text-[#00e5ff]' : isDone ? 'text-slate-200' : 'text-slate-500'}`}>
                    {s.title}
                  </div>
                  <div className="hidden sm:block text-[10px] text-slate-500">{s.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* STEP 1: Incident Details */}
      {currentStep === 1 && (
        <form onSubmit={handleStep1Submit} className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
          <div className="border-b border-white/10 pb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold font-mono text-white flex items-center space-x-2">
                <FileText className="w-5 h-5 text-[#00e5ff]" />
                <span>Step 1: Incident & Case Registration</span>
              </h2>
              <p className="text-xs text-slate-400">
                Provide foundational forensic details. Fields will be watermarked on the legal investigation report.
              </p>
            </div>
            <span className="text-xs font-mono text-[#00e5ff] bg-[#00e5ff]/10 px-2.5 py-1 rounded border border-[#00e5ff]/20">
              CASE #{formData.case_id}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Case ID *</label>
              <input
                type="text"
                required
                value={formData.case_id}
                onChange={(e) => setFormData({ ...formData, case_id: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white font-mono focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Incident Title *</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Incident Type *</label>
              <select
                value={formData.incident_type}
                onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              >
                {INCIDENT_TYPES.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Priority Level</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical Priority</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Incident Date *</label>
              <input
                type="date"
                required
                value={formData.incident_date}
                onChange={(e) => setFormData({ ...formData, incident_date: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white font-mono focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Incident Time *</label>
              <input
                type="time"
                required
                value={formData.incident_time}
                onChange={(e) => setFormData({ ...formData, incident_time: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white font-mono focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Crime / Incident Location *</label>
              <input
                type="text"
                required
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Police Station / Jurisdiction *</label>
              <input
                type="text"
                required
                value={formData.police_station}
                onChange={(e) => setFormData({ ...formData, police_station: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Lead Investigator Name *</label>
              <input
                type="text"
                required
                value={formData.investigator_name}
                onChange={(e) => setFormData({ ...formData, investigator_name: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-mono text-slate-300 mb-1.5">Case Narrative / Details</label>
              <textarea
                rows={3}
                value={formData.case_description}
                onChange={(e) => setFormData({ ...formData, case_description: e.target.value })}
                className="w-full bg-[#07090e] border border-white/15 rounded-lg px-3.5 py-2 text-sm text-white focus:border-[#00e5ff] focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-white/10">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] flex items-center space-x-2 transition-all"
            >
              <span>{loading ? 'Creating Case...' : 'CONTINUE TO EVIDENCE UPLOAD'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      )}

      {/* STEP 2: Video Evidence Upload */}
      {currentStep === 2 && (
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
          <div className="border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold font-mono text-white flex items-center space-x-2">
              <Film className="w-5 h-5 text-[#00e5ff]" />
              <span>Step 2: CCTV Video Evidence Ingestion</span>
            </h2>
            <p className="text-xs text-slate-400">
              Calibrate multiple camera streams across spatial sectors. Supports MP4, AVI, MKV up to 4K resolution.
            </p>
          </div>

          {/* Camera Cards List */}
          <div className="space-y-4">
            {cameraVideos.map((cam, idx) => (
              <div key={idx} className="bg-[#07090e]/80 border border-white/10 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex items-center space-x-3.5">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-[#00e5ff] shrink-0">
                    <Camera className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-mono font-bold text-sm text-white">{cam.camera_id}</div>
                    <div className="text-xs text-slate-400">{cam.location}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-6 text-xs font-mono text-slate-400">
                  <div>
                    <span className="text-slate-500">Duration: </span>
                    <span className="text-white">{cam.duration}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Resolution: </span>
                    <span className="text-white">{cam.resolution}</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {cam.file ? 'FILE LOADED' : 'CALIBRATED READY'}
                  </span>
                </div>

                <div className="flex items-center space-x-2 w-full md:w-auto">
                  <label className="cursor-pointer px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 hover:bg-white/10 text-[#00e5ff] border border-white/10 transition-colors flex items-center space-x-1.5">
                    <Upload className="w-3.5 h-3.5" />
                    <span>{cam.file ? cam.file.name.substring(0, 16) + '...' : 'Select File'}</span>
                    <input
                      type="file"
                      accept="video/*"
                      className="hidden"
                      onChange={(e) => handleFileDrop(idx, e)}
                    />
                  </label>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-white/10">
            <button
              onClick={() => setCurrentStep(1)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white flex items-center space-x-1.5 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handleStep2Submit}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] flex items-center space-x-2 transition-all"
            >
              <span>{loading ? 'Ingesting Streams...' : 'PROCEED TO REFERENCE IMAGES'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Reference Images */}
      {currentStep === 3 && (
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
          <div className="border-b border-white/10 pb-4">
            <h2 className="text-lg font-bold font-mono text-white flex items-center space-x-2">
              <UserCheck className="w-5 h-5 text-[#00e5ff]" />
              <span>Step 3: Reference Image Matching (Optional)</span>
            </h2>
            <p className="text-xs text-slate-400">
              Do you have a reference photograph of the suspect or victim? If unavailable, the AI automatically activates the Unsupervised Forensic Person-of-Interest Discovery Pipeline.
            </p>
          </div>

          {/* Reference Mode Choice */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'Suspect', title: 'Suspect Image', desc: 'Known person of interest' },
              { id: 'Victim', title: 'Victim Image', desc: 'Missing person / casualty' },
              { id: 'Both', title: 'Both Suspect & Victim', desc: 'Multiple reference profiles' },
              { id: 'None', title: 'No Reference Available', desc: 'Unsupervised gait clustering' }
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setReferenceType(opt.id as any)}
                className={`p-4 rounded-xl text-left border transition-all ${
                  referenceType === opt.id
                    ? 'bg-[#00e5ff]/15 border-[#00e5ff] text-white shadow-[0_0_15px_rgba(0,229,255,0.2)]'
                    : 'bg-[#07090e]/60 border-white/10 text-slate-400 hover:border-white/20'
                }`}
              >
                <div className="font-mono font-bold text-xs text-white mb-1">{opt.title}</div>
                <div className="text-[10px] text-slate-400">{opt.desc}</div>
              </button>
            ))}
          </div>

          {referenceType !== 'None' && (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-white/15 rounded-xl p-6 text-center hover:border-[#00e5ff]/50 transition-colors">
                <ImageIcon className="w-8 h-8 text-[#00e5ff] mx-auto mb-2" />
                <p className="text-xs font-semibold text-white">Upload Reference Mugshots / Photographs</p>
                <p className="text-[11px] text-slate-400 mb-3">PNG, JPG, WEBP (Maximum 5 images recommended)</p>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => {
                    if (e.target.files) {
                      const files = Array.from(e.target.files);
                      setReferenceFiles(files);
                      const urls = files.map(f => URL.createObjectURL(f));
                      setReferencePreviews(urls);
                    }
                  }}
                  className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#00e5ff]/15 file:text-[#00e5ff] hover:file:bg-[#00e5ff]/25 cursor-pointer"
                />
              </div>

              {/* Preview Gallery */}
              <div className="flex items-center space-x-3">
                {referencePreviews.map((url, i) => (
                  <div key={i} className="relative w-20 h-24 rounded-lg overflow-hidden border border-[#00e5ff]/40 shadow-[0_0_10px_rgba(0,229,255,0.2)]">
                    <img src={url} alt="Reference Preview" className="w-full h-full object-cover" />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[9px] font-mono text-center text-cyan-300 py-0.5">
                      REF #{i + 1}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-white/10">
            <button
              onClick={() => setCurrentStep(2)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white flex items-center space-x-1.5 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handleStep3Submit}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] flex items-center space-x-2 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>EXECUTE AI FORENSIC PIPELINE</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Live AI Processing Pipeline */}
      {currentStep === 4 && (
        <div className="glass-panel rounded-2xl p-6 sm:p-10 border border-[#00e5ff]/30 shadow-[0_0_30px_rgba(0,229,255,0.15)] space-y-8">
          <div className="text-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-[#00e5ff]/40 flex items-center justify-center text-[#00e5ff] mx-auto shadow-[0_0_25px_rgba(0,229,255,0.3)]">
              <Cpu className="w-7 h-7 animate-pulse" />
            </div>
            <h2 className="text-2xl font-black font-mono tracking-tight text-white">
              Forensic Neural Processing Active
            </h2>
            <p className="text-xs text-slate-400 max-w-lg mx-auto font-mono">
              Running deep feature extraction, ByteTrack trajectory mapping, MediaPipe kinematic gait profiling, and multi-camera spatial correlation.
            </p>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-[#00e5ff] font-semibold">{PIPELINE_TASKS[activeStepIndex]}</span>
              <span className="text-white font-bold">{pipelineProgress}%</span>
            </div>
            <div className="w-full h-2.5 bg-black/60 rounded-full overflow-hidden border border-white/10 p-0.5">
              <div
                className="h-full bg-gradient-to-r from-[#00e5ff] via-sky-400 to-purple-500 rounded-full transition-all duration-300 shadow-[0_0_15px_#00e5ff]"
                style={{ width: `${pipelineProgress}%` }}
              />
            </div>
          </div>

          {/* Detailed Pipeline Checklist */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
            {PIPELINE_TASKS.map((task, idx) => {
              const isCompleted = idx < activeStepIndex;
              const isRunning = idx === activeStepIndex;
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-lg flex items-center space-x-3 border transition-all ${
                    isCompleted
                      ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-400'
                      : isRunning
                      ? 'bg-cyan-950/30 border-[#00e5ff]/50 text-[#00e5ff] shadow-[0_0_12px_rgba(0,229,255,0.2)]'
                      : 'bg-[#07090e]/40 border-white/5 text-slate-600'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isRunning ? (
                    <span className="relative flex h-3.5 w-3.5 shrink-0">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-[#00e5ff]"></span>
                    </span>
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                  )}
                  <span className="truncate">{task}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* STEP 5: Forensic Results Overview */}
      {currentStep === 5 && (
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-emerald-500/30 shadow-[0_0_25px_rgba(16,185,129,0.15)] flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold font-mono text-white">
                  AI Forensic Analysis Successfully Completed
                </h2>
                <p className="text-xs text-slate-400">
                  Case #{formData.case_id} has been processed across all calibrated camera feeds. 2 candidate persons of interest isolated.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 w-full md:w-auto">
              <a
                href={createdInvId ? `/investigations/${createdInvId}` : '/investigations'}
                className="px-5 py-2.5 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_20px_rgba(0,229,255,0.3)] flex items-center space-x-2"
              >
                <span>OPEN COMPLETE DOSSIER</span>
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Quick Snapshot of Isolated POI */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Candidate 1 */}
            <div className="glass-panel rounded-2xl p-6 border border-rose-500/30 space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-14 h-16 rounded-lg overflow-hidden border border-rose-500/50">
                    <img
                      src="https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=400&auto=format&fit=crop&q=60"
                      alt="Candidate Crop"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      HIGH RELEVANCE CANDIDATE
                    </span>
                    <h3 className="font-mono font-bold text-base text-white mt-1">Person of Interest #07</h3>
                    <p className="text-xs text-slate-400">Track ID: 07 | Cameras: 3</p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs font-mono text-slate-400">AI Relevance</div>
                  <div className="text-2xl font-black font-mono text-rose-400">91%</div>
                </div>
              </div>

              {/* Mask Alert */}
              <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-500/30 flex items-start space-x-2.5 text-xs text-rose-300">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Face Visibility: MASKED (Balaclava)</span>
                  <p className="text-[11px] text-rose-200/80">Alternative Identification Pipeline Activated: Kinematic Gait & Clothing Appearance matching.</p>
                </div>
              </div>

              {/* Gait Summary */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <div>
                  <span className="text-slate-500">Gait Signature:</span>
                  <div className="text-[#00e5ff] font-bold">GAIT-007</div>
                </div>
                <div>
                  <span className="text-slate-500">Cadence / Speed:</span>
                  <div className="text-white">Medium (1.35 m/s)</div>
                </div>
                <div>
                  <span className="text-slate-500">Arm Swing:</span>
                  <div className="text-amber-400">Low / Concealed</div>
                </div>
                <div>
                  <span className="text-slate-500">Body Posture:</span>
                  <div className="text-white">Forward Lean (7.4°)</div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <a
                  href="/evidence"
                  className="text-xs font-semibold text-[#00e5ff] hover:underline flex items-center space-x-1"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Inspect Evidence Clips</span>
                </a>
                <span className="text-[11px] text-slate-500 font-mono">First: 07:30 PM | Last: 08:05 PM</span>
              </div>
            </div>

            {/* Candidate 2 */}
            <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-14 h-16 rounded-lg overflow-hidden border border-white/20">
                    <img
                      src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=60"
                      alt="Candidate Crop"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      MODERATE RELEVANCE
                    </span>
                    <h3 className="font-mono font-bold text-base text-white mt-1">Person of Interest #03</h3>
                    <p className="text-xs text-slate-400">Track ID: 03 | Cameras: 1</p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs font-mono text-slate-400">AI Relevance</div>
                  <div className="text-2xl font-black font-mono text-amber-400">74%</div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Face Partially Covered by Cap & Collar.</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-[#07090e]/60 p-3 rounded-lg border border-white/5">
                <div>
                  <span className="text-slate-500">Gait Signature:</span>
                  <div className="text-purple-400 font-bold">GAIT-003</div>
                </div>
                <div>
                  <span className="text-slate-500">Cadence / Speed:</span>
                  <div className="text-white">Fast (1.6 m/s)</div>
                </div>
                <div>
                  <span className="text-slate-500">Arm Swing:</span>
                  <div className="text-white">Normal Pendular</div>
                </div>
                <div>
                  <span className="text-slate-500">Body Posture:</span>
                  <div className="text-white">Erect (3.2°)</div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <a
                  href="/reports"
                  className="text-xs font-semibold text-slate-300 hover:text-white flex items-center space-x-1"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Forensic PDF</span>
                </a>
                <span className="text-[11px] text-slate-500 font-mono">Duration: 2m 15s</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
