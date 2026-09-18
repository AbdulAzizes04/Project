'use client';

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Video,
  Users,
  Film,
  FileCheck,
  AlertCircle,
  TrendingUp,
  ArrowRight,
  Sparkles,
  Search,
  Eye,
  Activity,
  Clock,
  MapPin,
  Camera
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { fetchDashboardStats, seedDemoCase } from '@/lib/api';
import { DashboardStats } from '@/lib/types';

const HOURLY_ACTIVITY = [
  { hour: '14:00', detections: 12, alerts: 1 },
  { hour: '15:00', detections: 19, alerts: 2 },
  { hour: '16:00', detections: 28, alerts: 3 },
  { hour: '17:00', detections: 45, alerts: 4 },
  { hour: '18:00', detections: 62, alerts: 7 },
  { hour: '19:00', detections: 89, alerts: 14 },
  { hour: '20:00', detections: 74, alerts: 9 },
  { hour: '21:00', detections: 38, alerts: 5 },
];

const INCIDENT_BREAKDOWN = [
  { name: 'Theft / Heist', count: 35, color: '#ef4444' },
  { name: 'Perimeter Breach', count: 28, color: '#f59e0b' },
  { name: 'Suspicious Activity', count: 22, color: '#00e5ff' },
  { name: 'Vehicle Crime', count: 15, color: '#9333ea' },
];

const MASK_STATS = [
  { name: 'Masked (Balaclava/Cover)', value: 42, color: '#ef4444' },
  { name: 'Partially Occluded', value: 28, color: '#f59e0b' },
  { name: 'Fully Visible Face', value: 30, color: '#10b981' },
];

export default function DashboardView() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchDashboardStats();
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Completed':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Completed</span>;
      case 'Processing':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/15 text-[#00e5ff] border border-cyan-500/30 animate-pulse">Processing</span>;
      case 'Failed':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-500/15 text-red-400 border border-red-500/30">Failed</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">Pending</span>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner / Intelligence Header */}
      <div className="relative rounded-2xl p-6 md:p-8 overflow-hidden bg-gradient-to-br from-[#111625] via-[#0c101c] to-[#07090e] border border-white/10 shadow-2xl">
        <div className="absolute -right-16 -top-16 w-80 h-80 rounded-full bg-[#00e5ff]/10 blur-3xl pointer-events-none" />
        <div className="absolute right-1/4 -bottom-20 w-72 h-72 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#00e5ff] shadow-[0_0_10px_#00e5ff]" />
              <span className="text-xs font-mono font-semibold tracking-widest text-[#00e5ff] uppercase">
                Forensic Command Console
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-white font-mono">
              VisionTrace <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-purple-400">AI</span>
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl">
              Intelligent Forensic Surveillance Platform for Smart Crime Investigation, Person of Interest Tracking, Kinematic Gait Profiling, and Rapid Evidentiary Analysis.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <a
              href="/investigations/new"
              className="px-5 py-2.5 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_20px_rgba(0,229,255,0.35)] transition-all flex items-center space-x-2"
            >
              <span>CREATE INVESTIGATION</span>
              <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="/search"
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10 transition-colors flex items-center space-x-2"
            >
              <Search className="w-4 h-4 text-[#00e5ff]" />
              <span>Forensic Query</span>
            </a>
          </div>
        </div>
      </div>

      {/* 5 Primary Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Stat 1 */}
        <div className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">Active Investigations</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-white">
              {stats?.active_investigations ?? 0}
            </span>
            <span className="text-[11px] font-mono text-emerald-400 flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> +2 this wk
            </span>
          </div>
        </div>

        {/* Stat 2 */}
        <div className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">Videos Processed</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-[#00e5ff]">
              <Video className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-white">
              {stats?.total_videos_processed ?? 0}
            </span>
            <span className="text-[11px] font-mono text-cyan-400">1080p Calibrated</span>
          </div>
        </div>

        {/* Stat 3 */}
        <div className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">Persons Detected</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-white">
              {stats?.persons_detected ?? 0}
            </span>
            <span className="text-[11px] font-mono text-purple-400">ByteTrack Tracked</span>
          </div>
        </div>

        {/* Stat 4 */}
        <div className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">Evidence Items</span>
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400">
              <Film className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-white">
              {stats?.evidence_items ?? 0}
            </span>
            <span className="text-[11px] font-mono text-slate-400">Clips & Frames</span>
          </div>
        </div>

        {/* Stat 5 */}
        <div className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">Reports Generated</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-white">
              {stats?.reports_generated ?? 1}
            </span>
            <span className="text-[11px] font-mono text-emerald-400">Court Export Ready</span>
          </div>
        </div>
      </div>

      {/* Forensic Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Surveillance Activity Timeline */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-bold text-white font-mono">
                Real-Time Surveillance Activity Stream
              </h3>
              <p className="text-xs text-slate-400">
                Hourly person detections vs. suspicious anomaly alerts across calibrated cameras
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-md text-[11px] font-mono bg-white/5 text-slate-300 border border-white/10">
              UTC FEED
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={HOURLY_ACTIVITY} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00e5ff" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00e5ff" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#00e5ff' }}
                />
                <Area type="monotone" dataKey="detections" stroke="#00e5ff" strokeWidth={2} fillOpacity={1} fill="url(#colorDetections)" name="Persons Tracked" />
                <Area type="monotone" dataKey="alerts" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorAlerts)" name="Suspicious Alerts" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Mask Occlusion & Gait Pipeline Trigger */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white font-mono">
                Facial Visibility & Mask Ratio
              </h3>
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            </div>
            <p className="text-xs text-slate-400 mb-4">
              When facial biometrics are obscured, the Alternative Gait & Appearance Pipeline is automatically engaged.
            </p>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={MASK_STATS}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={68}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {MASK_STATS.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-white/5 font-mono text-xs">
            {MASK_STATS.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-slate-300">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="truncate max-w-[170px]">{item.name}</span>
                </div>
                <span className="font-bold text-white">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Investigations Table */}
      <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-white font-mono flex items-center space-x-2">
              <span>Recent Forensic Investigations</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-white/10 text-slate-300">ACTIVE DOSSIERS</span>
            </h3>
            <p className="text-xs text-slate-400">
              Active crime files undergoing multi-camera tracking, timeline generation, and candidate isolation
            </p>
          </div>
          <a
            href="/investigations"
            className="text-xs font-semibold text-[#00e5ff] hover:underline flex items-center space-x-1"
          >
            <span>View All Investigations</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-sans text-xs">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 font-mono">
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Incident Details</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Date Recorded</th>
                <th className="py-3 px-4">Streams</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-200">
              {stats?.recent_investigations && stats.recent_investigations.length > 0 ? (
                stats.recent_investigations.map((inv) => (
                  <tr key={inv.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="py-3.5 px-4 font-mono font-bold text-[#00e5ff] flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#00e5ff]" />
                      <span>{inv.case_id}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white">{inv.title}</div>
                      <div className="text-[11px] text-slate-400">{inv.incident_type}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <div className="flex items-center space-x-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        <span className="truncate max-w-[180px]">{inv.location}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {inv.date}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      <div className="flex items-center space-x-1">
                        <Camera className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{inv.videos_count} cams</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      {getStatusBadge(inv.status)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <a
                        href={`/investigations/${inv.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-md font-semibold text-[11px] bg-white/5 hover:bg-[#00e5ff]/20 hover:text-[#00e5ff] text-slate-300 border border-white/10 transition-all"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect Dossier</span>
                      </a>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-400">
                    No investigations currently active. Click "Load Viva Demo" or "Create Investigation" to begin.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
