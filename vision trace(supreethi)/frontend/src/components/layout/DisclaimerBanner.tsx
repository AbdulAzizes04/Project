'use client';

import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="w-full bg-gradient-to-r from-amber-950/40 via-[#131826] to-amber-950/40 border-y border-amber-500/20 px-4 py-2 text-xs font-mono text-amber-300 flex items-center justify-between no-print">
      <div className="max-w-7xl mx-auto w-full flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center space-x-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <p>
            <span className="font-bold text-amber-200">AI-ASSISTED FORENSIC NOTICE:</span>{' '}
            Identifications, gait kinematics, and similarity metrics represent probabilistic candidates. Human investigator verification is mandatory.
          </p>
        </div>
        <div className="flex items-center space-x-3 text-[11px] text-slate-400">
          <span className="flex items-center space-x-1 text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Forensic Chain of Custody</span>
          </span>
          <span className="hidden md:inline text-white/20">|</span>
          <span className="hidden md:inline">ISO/IEC 27037 Compliant Architecture</span>
        </div>
      </div>
    </div>
  );
}
