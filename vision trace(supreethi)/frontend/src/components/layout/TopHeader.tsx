'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { ShieldCheck, Search, Radio, Bell } from 'lucide-react';

export default function TopHeader() {
  const pathname = usePathname();

  const getPageTitle = (path: string) => {
    if (path.startsWith('/investigations/new')) return 'New Forensic Investigation Wizard';
    if (path.startsWith('/investigations/')) return 'Investigation Dossier & Candidate Hub';
    if (path.startsWith('/investigations')) return 'Investigation Archive & Registry';
    if (path.startsWith('/evidence')) return 'Forensic Evidence Video Player & CLAHE Enhancer';
    if (path.startsWith('/search')) return 'Natural Language Surveillance Search';
    if (path.startsWith('/reports')) return 'Court-Admissible Forensic Reports';
    return 'Surveillance Intelligence Hub';
  };

  return (
    <div className="border-b border-white/10 bg-[#07090e]/80 backdrop-blur-md px-4 sm:px-8 py-3.5 flex items-center justify-between no-print">
      <div className="flex items-center space-x-3">
        <span className="font-mono text-xs font-bold text-slate-400 uppercase tracking-widest hidden sm:inline">
          CONSOLE //
        </span>
        <h2 className="text-sm font-bold text-white font-mono">
          {getPageTitle(pathname)}
        </h2>
      </div>

      <div className="flex items-center space-x-4">
        <a
          href="/search"
          className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-mono text-slate-400 hover:text-white transition-colors"
        >
          <Search className="w-3.5 h-3.5 text-[#00e5ff]" />
          <span>Quick Query (/)</span>
        </a>

        <div className="flex items-center space-x-2 text-xs font-mono text-emerald-400 bg-emerald-950/30 px-2.5 py-1 rounded-lg border border-emerald-500/30">
          <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
          <span className="hidden md:inline">3 Cameras Calibrated</span>
        </div>
      </div>
    </div>
  );
}
