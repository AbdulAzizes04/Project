'use client';

import React, { useState, useEffect } from 'react';
import {
  Layers,
  Search,
  Filter,
  PlusCircle,
  Eye,
  MapPin,
  Calendar,
  Camera,
  Shield,
  Clock,
  Sparkles
} from 'lucide-react';
import { fetchInvestigations, seedDemoCase } from '@/lib/api';
import { Investigation } from '@/lib/types';

export default function InvestigationsDirectoryPage() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchInvestigations();
        setInvestigations(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = investigations.filter((inv) => {
    const matchesQuery =
      inv.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (inv.incident?.location || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'All' || inv.status === statusFilter;
    return matchesQuery && matchesStatus;
  });

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-[#00e5ff]" />
            <span className="text-xs font-mono font-semibold tracking-widest text-[#00e5ff] uppercase">
              CASE ARCHIVE & REGISTRY
            </span>
          </div>
          <h1 className="text-2xl font-black font-mono tracking-tight text-white mt-1">
            Forensic Investigation Dossiers
          </h1>
          <p className="text-xs text-slate-400">
            Chronological log of forensic surveillance operations and multi-camera evidence analyses
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={async () => {
              await seedDemoCase();
              window.location.reload();
            }}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-purple-950/40 text-purple-300 border border-purple-500/30 hover:bg-purple-900/50 transition-colors flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>Load Demo Case</span>
          </button>

          <a
            href="/investigations/new"
            className="px-4 py-2 rounded-xl font-bold text-xs tracking-wide bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] transition-all flex items-center space-x-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>NEW DOSSIER</span>
          </a>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Case ID, title, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#07090e] border border-white/15 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-[#00e5ff] focus:outline-none"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          {['All', 'Completed', 'Processing', 'Pending'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                statusFilter === status
                  ? 'bg-[#00e5ff]/15 text-[#00e5ff] border border-[#00e5ff]/30 font-semibold'
                  : 'text-slate-400 hover:text-white bg-white/5'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Investigations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((inv) => (
          <div
            key={inv.id}
            className="glass-panel rounded-xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all flex flex-col justify-between group"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-[#00e5ff] bg-[#00e5ff]/10 px-2 py-0.5 rounded border border-[#00e5ff]/20">
                  {inv.case_id}
                </span>
                {getStatusBadge(inv.status)}
              </div>

              <div>
                <h3 className="text-sm font-bold text-white group-hover:text-[#00e5ff] transition-colors line-clamp-1">
                  {inv.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                  {inv.incident?.case_description || 'Investigative surveillance footage logged and calibrated for automated feature identification.'}
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-400 pt-2 border-t border-white/5">
                <div className="flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span className="truncate">{inv.incident?.location || 'Central Sector'}</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span>{inv.incident?.incident_date || '2026-09-08'} at {inv.incident?.incident_time || '19:30'}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between">
              <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
                <span className="flex items-center space-x-1">
                  <Camera className="w-3 h-3 text-cyan-400" />
                  <span>{inv.videos?.length || 3} Cams</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Shield className="w-3 h-3 text-purple-400" />
                  <span>{inv.detected_persons?.length || 2} POIs</span>
                </span>
              </div>

              <a
                href={`/investigations/${inv.id}`}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 hover:bg-[#00e5ff]/20 hover:text-[#00e5ff] text-slate-200 border border-white/10 transition-all flex items-center space-x-1"
              >
                <Eye className="w-3 h-3" />
                <span>Open Dossier</span>
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
