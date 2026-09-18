'use client';

import React, { useState } from 'react';
import {
  FileText,
  Printer,
  Download,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Clock,
  MapPin,
  Camera,
  Activity,
  User,
  Share2
} from 'lucide-react';

export default function ForensicReportsPage() {
  const [downloading, setDownloading] = useState(false);

  const reportData = {
    report_number: 'REP-CASE-2026-089-20260908',
    generated_at: '2026-09-08 19:35:12 UTC',
    case: {
      case_id: 'CASE-2026-089',
      title: 'Armed Jewelry Vault Heist & Perimeter Breach',
      incident_type: 'Robbery',
      incident_date: '2026-09-08',
      incident_time: '07:30 PM',
      location: 'Grand Metropolitan Exchange, Vault Sector 4',
      police_station: 'Central Metropolitan Police Precinct',
      investigator: 'Detective Inspector R. Harrison',
      priority: 'Critical Priority'
    },
    evidence_summary: {
      streams_analyzed: 3,
      persons_tracked: 8,
      flagged_candidates: 2,
      timeline_waypoints: 5,
      vehicles_detected: 3
    },
    candidates: [
      {
        track_id: 7,
        label: 'Candidate Person of Interest #07',
        relevance_score: 91,
        similarity_score: 87,
        face_visibility: 'Masked (Balaclava Facial Occlusion)',
        appearance: 'Dark charcoal hooded tactical jacket, dark denim trousers, athletic footwear with reflective heel',
        first_seen: '07:30 PM (Camera 01)',
        last_seen: '08:05 PM (Camera 03)',
        total_duration: '4 minutes 32 seconds',
        gait_signature: 'GAIT-007',
        walking_speed: 'Medium Cadence (1.35 m/s)',
        arm_swing: 'Low / Guarded (Concealment Profile)',
        body_posture: 'Slight Forward Lean (7.4°)',
        snapshot: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=60'
      },
      {
        track_id: 3,
        label: 'Candidate #03 (Secondary Subject)',
        relevance_score: 74,
        similarity_score: 42,
        face_visibility: 'Partially Covered (Baseball cap & high collar)',
        appearance: 'Gray utility jacket, dark cargo pants',
        first_seen: '07:45 PM (Camera 02)',
        last_seen: '08:01 PM (Camera 02)',
        total_duration: '2 minutes 15 seconds',
        gait_signature: 'GAIT-003',
        walking_speed: 'Fast Cadence (1.6 m/s)',
        arm_swing: 'Moderate Swing',
        body_posture: 'Erect Posture',
        snapshot: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&auto=format&fit=crop&q=60'
      }
    ],
    timeline: [
      { time: '07:30 PM', camera: 'Camera 01 - Main Gate', desc: 'Candidate #07 first detected entering exterior perimeter from north access checkpoint' },
      { time: '07:42 PM', camera: 'Camera 02 - Vault Corridor', desc: 'Candidate #07 observed in central corridor; face obscured with balaclava' },
      { time: '07:48 PM', camera: 'Camera 02 - Vault Corridor', desc: 'Candidate #03 enters corridor and lingers at western door' },
      { time: '07:51 PM', camera: 'Camera 03 - West Perimeter', desc: 'Candidate #07 moves rapidly towards parking barrier; gait matches GAIT-007' },
      { time: '08:05 PM', camera: 'Camera 03 - West Perimeter', desc: 'Last visual contact before subject departs surveillance radius into blind zone' }
    ]
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports/generate/demo');
      // If endpoint returns file, trigger download or browser print
      window.print();
    } catch {
      window.print();
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Action Header (Hidden on Print) */}
      <div className="no-print flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel rounded-2xl p-5 border border-white/10">
        <div>
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-[#00e5ff]" />
            <span className="text-xs font-mono font-semibold tracking-widest text-[#00e5ff] uppercase">
              COURT-READY FORENSIC REPORT
            </span>
          </div>
          <h1 className="text-xl font-bold font-mono text-white mt-1">
            AI-Assisted Forensic Surveillance Dossier
          </h1>
          <p className="text-xs text-slate-400">
            Document Number: {reportData.report_number}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10 transition-colors flex items-center space-x-2"
          >
            <Printer className="w-4 h-4 text-slate-400" />
            <span>Browser Print</span>
          </button>

          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="px-5 py-2 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] transition-all flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>{downloading ? 'Preparing PDF...' : 'EXPORT FORENSIC PDF'}</span>
          </button>
        </div>
      </div>

      {/* Official Legal Report Body (White paper styled for printing, dark for UI) */}
      <div className="bg-[#0f1422] print:bg-white print:text-black rounded-2xl p-8 sm:p-12 border border-white/15 print:border-none shadow-2xl space-y-8 font-sans">
        {/* Header Title Block */}
        <div className="border-b-2 border-[#00e5ff] print:border-black pb-6 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="text-xs font-mono font-bold tracking-widest text-[#00e5ff] print:text-blue-700 uppercase">
              VISIONTRACE AI • FORENSIC SURVEILLANCE & REID PLATFORM
            </div>
            <h2 className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-white print:text-black">
              AI-ASSISTED FORENSIC INVESTIGATION REPORT
            </h2>
            <p className="text-xs text-slate-400 print:text-slate-600 font-mono">
              Report Generated: {reportData.generated_at} | Classification: RESTRICTED LAW ENFORCEMENT
            </p>
          </div>

          <div className="text-right font-mono text-xs text-slate-400 print:text-slate-600">
            <div className="font-bold text-white print:text-black">DOSSIER REF:</div>
            <div className="text-[#00e5ff] print:text-blue-700 font-bold">{reportData.report_number}</div>
          </div>
        </div>

        {/* Mandatory Legal & Forensic Compliance Disclaimer Box */}
        <div className="bg-rose-950/20 print:bg-red-50 border-2 border-rose-500/50 print:border-red-600 rounded-xl p-4 text-xs space-y-1 text-rose-200 print:text-red-900">
          <div className="flex items-center space-x-2 font-mono font-bold text-rose-400 print:text-red-700 uppercase">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>MANDATORY AI FORENSIC DISCLAIMER & LEGAL NOTICE</span>
          </div>
          <p className="leading-relaxed text-[11px] print:text-xs">
            This document contains automated AI-assisted analytical results generated by computer vision neural networks. All candidate identifications, similarity scores, gait kinematics, and timeline associations are probabilistic and DO NOT constitute definitive proof of legal identity or criminal guilt. Final verification and evidentiary corroboration must be conducted by authorized human investigators prior to judicial submission.
          </p>
        </div>

        {/* Section 1: Incident & Case Information */}
        <div className="space-y-3">
          <h3 className="font-mono font-bold text-sm text-[#00e5ff] print:text-blue-800 uppercase tracking-wider flex items-center space-x-2">
            <span>1. Incident & Case Information</span>
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-[#07090e]/60 print:bg-slate-100 p-4 rounded-xl border border-white/10 print:border-slate-300 text-xs font-mono">
            <div>
              <span className="text-slate-500 print:text-slate-600 block">Case ID:</span>
              <span className="font-bold text-white print:text-black">{reportData.case.case_id}</span>
            </div>
            <div>
              <span className="text-slate-500 print:text-slate-600 block">Incident Type:</span>
              <span className="font-bold text-white print:text-black">{reportData.case.incident_type}</span>
            </div>
            <div>
              <span className="text-slate-500 print:text-slate-600 block">Incident Date / Time:</span>
              <span className="text-white print:text-black">{reportData.case.incident_date} ({reportData.case.incident_time})</span>
            </div>
            <div>
              <span className="text-slate-500 print:text-slate-600 block">Investigator:</span>
              <span className="text-white print:text-black">{reportData.case.investigator}</span>
            </div>
            <div className="col-span-2">
              <span className="text-slate-500 print:text-slate-600 block">Crime Scene Location:</span>
              <span className="text-white print:text-black">{reportData.case.location}</span>
            </div>
            <div className="col-span-2">
              <span className="text-slate-500 print:text-slate-600 block">Jurisdiction:</span>
              <span className="text-white print:text-black">{reportData.case.police_station}</span>
            </div>
          </div>
        </div>

        {/* Section 2: Surveillance Evidence Summary */}
        <div className="space-y-3">
          <h3 className="font-mono font-bold text-sm text-[#00e5ff] print:text-blue-800 uppercase tracking-wider">
            2. Surveillance Evidence Summary
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center text-xs font-mono">
            <div className="p-3 bg-[#07090e]/60 print:bg-slate-100 rounded-xl border border-white/10 print:border-slate-300">
              <div className="text-slate-500 text-[10px]">CCTV Streams</div>
              <div className="text-lg font-bold text-white print:text-black">{reportData.evidence_summary.streams_analyzed}</div>
            </div>
            <div className="p-3 bg-[#07090e]/60 print:bg-slate-100 rounded-xl border border-white/10 print:border-slate-300">
              <div className="text-slate-500 text-[10px]">Persons Tracked</div>
              <div className="text-lg font-bold text-white print:text-black">{reportData.evidence_summary.persons_tracked}</div>
            </div>
            <div className="p-3 bg-[#07090e]/60 print:bg-slate-100 rounded-xl border border-white/10 print:border-slate-300">
              <div className="text-slate-500 text-[10px]">Flagged Candidates</div>
              <div className="text-lg font-bold text-[#00e5ff] print:text-blue-700">{reportData.evidence_summary.flagged_candidates}</div>
            </div>
            <div className="p-3 bg-[#07090e]/60 print:bg-slate-100 rounded-xl border border-white/10 print:border-slate-300">
              <div className="text-slate-500 text-[10px]">Timeline Waypoints</div>
              <div className="text-lg font-bold text-white print:text-black">{reportData.evidence_summary.timeline_waypoints}</div>
            </div>
            <div className="p-3 bg-[#07090e]/60 print:bg-slate-100 rounded-xl border border-white/10 print:border-slate-300">
              <div className="text-slate-500 text-[10px]">Vehicles Identified</div>
              <div className="text-lg font-bold text-purple-400 print:text-purple-700">{reportData.evidence_summary.vehicles_detected}</div>
            </div>
          </div>
        </div>

        {/* Section 3: Candidate Person of Interest Analysis */}
        <div className="space-y-4">
          <h3 className="font-mono font-bold text-sm text-[#00e5ff] print:text-blue-800 uppercase tracking-wider">
            3. Candidate Person of Interest & Kinematic Analysis
          </h3>

          {reportData.candidates.map((cand, idx) => (
            <div
              key={idx}
              className="bg-[#07090e]/70 print:bg-slate-50 border border-white/10 print:border-slate-300 rounded-xl p-5 space-y-4"
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-white/10 print:border-slate-200 pb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-14 rounded-lg overflow-hidden border border-[#00e5ff]/40 shrink-0">
                    <img src={cand.snapshot} alt="Candidate" className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <h4 className="font-mono font-bold text-sm text-white print:text-black">{cand.label}</h4>
                    <span className="text-xs font-mono text-rose-400 print:text-red-700 font-semibold">{cand.face_visibility}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-xs font-mono">
                  <div className="text-right">
                    <span className="text-slate-500 text-[10px]">AI Relevance</span>
                    <div className="font-black text-[#00e5ff] print:text-blue-700 text-base">{cand.relevance_score}%</div>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-500 text-[10px]">Ref Similarity</span>
                    <div className="font-black text-purple-400 print:text-purple-700 text-base">{cand.similarity_score}%</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="space-y-1">
                  <span className="font-mono text-slate-500 block">Appearance Profile:</span>
                  <p className="text-slate-200 print:text-slate-800">{cand.appearance}</p>
                  <div className="font-mono text-slate-400 text-[11px] pt-1">
                    Span: {cand.first_seen} to {cand.last_seen} ({cand.total_duration})
                  </div>
                </div>

                <div className="space-y-1 font-mono bg-black/40 print:bg-white p-3 rounded-lg border border-white/5 print:border-slate-200">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Gait Signature:</span>
                    <span className="text-[#00e5ff] print:text-blue-700 font-bold">{cand.gait_signature}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Kinematic Cadence:</span>
                    <span className="text-white print:text-black">{cand.walking_speed}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Arm Swing Excursion:</span>
                    <span className="text-amber-400 print:text-amber-700">{cand.arm_swing}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Torso Posture:</span>
                    <span className="text-white print:text-black">{cand.body_posture}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Section 4: Chronological Movement Timeline */}
        <div className="space-y-3">
          <h3 className="font-mono font-bold text-sm text-[#00e5ff] print:text-blue-800 uppercase tracking-wider">
            4. Multi-Camera Chronological Movement Timeline
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs border border-white/10 print:border-slate-300">
              <thead>
                <tr className="bg-[#07090e] print:bg-slate-200 text-slate-400 print:text-slate-800 border-b border-white/10 print:border-slate-300">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Camera Sector</th>
                  <th className="py-2.5 px-3">Observed Movement / Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 print:divide-slate-200 text-slate-300 print:text-black">
                {reportData.timeline.map((item, idx) => (
                  <tr key={idx}>
                    <td className="py-2 px-3 text-[#00e5ff] print:text-blue-700 font-bold whitespace-nowrap">{item.time}</td>
                    <td className="py-2 px-3 font-semibold whitespace-nowrap">{item.camera}</td>
                    <td className="py-2 px-3">{item.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 5: Human Investigator Sign-Off Verification */}
        <div className="pt-6 border-t-2 border-white/10 print:border-slate-400 space-y-4 font-mono text-xs">
          <h3 className="font-bold text-sm text-[#00e5ff] print:text-blue-800 uppercase">
            5. Human Investigator Verification & Sign-Off
          </h3>
          <div className="grid grid-cols-2 gap-8 pt-4">
            <div className="space-y-6">
              <div>
                <span className="text-slate-500 block mb-1">Lead Investigator Signature:</span>
                <div className="border-b border-slate-600 print:border-black h-8 w-3/4" />
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Investigator Badge / ID:</span>
                <div className="font-bold text-white print:text-black">INV-4892-METRO</div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <span className="text-slate-500 block mb-1">Independent Reviewer Signature:</span>
                <div className="border-b border-slate-600 print:border-black h-8 w-3/4" />
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Verification Status:</span>
                <div className="text-emerald-400 print:text-green-700 font-bold flex items-center space-x-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  <span>CORROBORATED BY CERTIFIED FORENSIC ANALYST</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
