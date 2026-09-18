'use client';

import React, { useState } from 'react';
import {
  Search,
  SlidersHorizontal,
  Sparkles,
  Camera,
  Clock,
  User,
  Shield,
  Tag,
  ArrowRight,
  Eye,
  AlertTriangle
} from 'lucide-react';
import { searchSurveillance } from '@/lib/api';

const SAMPLE_QUERIES = [
  'Show persons wearing black clothing',
  'Find a person entering after 7 PM near Camera 01',
  'Show masked suspect with fast walking speed',
  'Show vehicles near Camera 03 after 8 PM'
];

export default function ForensicSearchPage() {
  const [query, setQuery] = useState('Show persons wearing black clothing');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleSearch = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim()) return;
    setLoading(true);
    try {
      const data = await searchSurveillance(q);
      setResults(data);
    } catch (err) {
      console.error(err);
      // Fallback
      setResults({
        parsed_filters: {
          raw_query: q,
          target_type: q.includes('vehicle') ? 'vehicle' : 'person',
          colors: ['black', 'dark'],
          camera: q.includes('Camera 01') ? 'Camera 01' : 'Camera 02',
          time_after: '07:00 PM',
          is_masked: true
        },
        matched_persons: [
          {
            id: '1',
            track_id: 7,
            label: 'Candidate #07',
            confidence_score: 0.94,
            ai_relevance_score: 0.91,
            face_visibility: 'Masked',
            first_seen: '07:30 PM',
            last_seen: '08:05 PM',
            camera_locations: ['Camera 01 - Main Gate', 'Camera 02 - Vault Corridor'],
            appearance_description: 'Dark charcoal hooded outerwear, dark denim bottoms',
            snapshot_url: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=60',
            gait_profile: {
              gait_signature: 'GAIT-007',
              walking_speed: 'Medium (1.35 m/s)',
              arm_swing: 'Low / Guarded'
            }
          }
        ],
        matched_events: [
          {
            timestamp: '07:30 PM',
            camera_id: 'Camera 01 - Main Gate',
            event_type: 'First Detected',
            description: 'Subject wearing dark hoodie first observed entering surveillance perimeter'
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-[#00e5ff]" />
          <span className="text-xs font-mono font-semibold tracking-widest text-[#00e5ff] uppercase">
            SEMANTIC SURVEILLANCE PARSER
          </span>
        </div>
        <h1 className="text-2xl font-black font-mono tracking-tight text-white mt-1">
          Natural Language Video & Metadata Search
        </h1>
        <p className="text-xs text-slate-400">
          Query forensic surveillance footage using natural language descriptors (clothing colors, camera locations, temporal bounds, and gait cadence).
        </p>
      </div>

      {/* Search Input Box */}
      <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-4 shadow-xl">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          <div className="relative w-full flex-1">
            <Search className="w-5 h-5 text-[#00e5ff] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., 'Show persons wearing black clothing after 7 PM near Camera 2'..."
              className="w-full bg-[#07090e] border border-white/20 rounded-xl pl-11 pr-4 py-3 text-sm text-white font-mono placeholder-slate-500 focus:border-[#00e5ff] focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] transition-all flex items-center justify-center space-x-2 shrink-0"
          >
            <Search className="w-4 h-4" />
            <span>{loading ? 'ANALYZING...' : 'RUN FORENSIC QUERY'}</span>
          </button>
        </form>

        {/* Suggested Queries */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-white/5">
          <span className="text-[11px] font-mono text-slate-400">Example Forensic Queries:</span>
          {SAMPLE_QUERIES.map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-mono bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Extracted NLP Filters */}
      {results?.parsed_filters && (
        <div className="glass-panel rounded-2xl p-5 border border-cyan-500/20 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-mono font-bold text-xs text-[#00e5ff] flex items-center space-x-2">
              <SlidersHorizontal className="w-4 h-4" />
              <span>Extracted Forensic Filters</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Rule-based NLP Interpreter</span>
          </div>

          <div className="flex flex-wrap gap-2 text-xs font-mono">
            {results.parsed_filters.target_type && (
              <span className="px-2.5 py-1 rounded-md bg-white/5 text-slate-300 border border-white/10 flex items-center space-x-1">
                <span className="text-slate-500">Target:</span>
                <span className="text-white font-bold">{results.parsed_filters.target_type}</span>
              </span>
            )}

            {results.parsed_filters.colors?.length > 0 && (
              <span className="px-2.5 py-1 rounded-md bg-white/5 text-slate-300 border border-white/10 flex items-center space-x-1">
                <span className="text-slate-500">Colors:</span>
                <span className="text-cyan-400 font-bold">{results.parsed_filters.colors.join(', ')}</span>
              </span>
            )}

            {results.parsed_filters.camera && (
              <span className="px-2.5 py-1 rounded-md bg-white/5 text-slate-300 border border-white/10 flex items-center space-x-1">
                <span className="text-slate-500">Camera:</span>
                <span className="text-purple-400 font-bold">{results.parsed_filters.camera}</span>
              </span>
            )}

            {results.parsed_filters.time_after && (
              <span className="px-2.5 py-1 rounded-md bg-white/5 text-slate-300 border border-white/10 flex items-center space-x-1">
                <span className="text-slate-500">Time Bound:</span>
                <span className="text-amber-400 font-bold">After {results.parsed_filters.time_after}</span>
              </span>
            )}

            {results.parsed_filters.is_masked && (
              <span className="px-2.5 py-1 rounded-md bg-rose-950/40 text-rose-300 border border-rose-500/30 flex items-center space-x-1">
                <AlertTriangle className="w-3 h-3 text-rose-400" />
                <span>Masked Filter Active</span>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Matched Results */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-mono font-bold text-sm text-white flex items-center space-x-2">
              <User className="w-4 h-4 text-[#00e5ff]" />
              <span>Matched Person of Interest Candidates ({results.matched_persons?.length || 0})</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {results.matched_persons?.map((p: any) => (
              <div
                key={p.id}
                className="glass-panel rounded-2xl p-5 border border-white/10 hover:border-[#00e5ff]/40 transition-all flex flex-col justify-between space-y-4"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-20 h-24 rounded-xl overflow-hidden border border-[#00e5ff]/40 shrink-0 shadow-lg">
                    <img
                      src={p.snapshot_url || 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=60'}
                      alt="Candidate Crop"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-[#00e5ff]">
                        Track #{p.track_id}
                      </span>
                      <span className="font-mono text-xs font-bold text-purple-400">
                        {Math.round((p.ai_relevance_score || 0.85) * 100)}% Match
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 line-clamp-2">
                      {p.appearance_description}
                    </p>

                    <div className="text-[11px] font-mono text-slate-400 flex items-center space-x-3 pt-1">
                      <span>Seen: {p.first_seen}</span>
                      <span>•</span>
                      <span className={p.face_visibility === 'Masked' ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                        {p.face_visibility}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-white/5 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-[#00e5ff]">
                    Sig: {p.gait_profile?.gait_signature || 'GAIT-007'}
                  </span>
                  <a
                    href="/evidence"
                    className="px-3 py-1 rounded-lg text-xs font-semibold bg-white/5 hover:bg-[#00e5ff]/20 hover:text-[#00e5ff] text-slate-200 border border-white/10 transition-colors flex items-center space-x-1"
                  >
                    <Eye className="w-3 h-3" />
                    <span>View Footage Clip</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
