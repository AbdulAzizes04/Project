'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import {
  ShieldAlert,
  Video,
  FileText,
  Search,
  Car,
  PlusCircle,
  Cpu,
  Sparkles,
  Activity,
  Layers,
  Shield,
  Clock,
  Radio,
  Menu,
  X,
  ChevronRight
} from 'lucide-react';
import { seedDemoCase } from '@/lib/api';

export default function Sidebar() {
  const pathname = usePathname();
  const [time, setTime] = useState<string>('');
  const [seeding, setSeeding] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await seedDemoCase();
      window.location.reload();
    } catch (err) {
      console.error(err);
    } finally {
      setSeeding(false);
    }
  };

  const navGroups = [
    {
      title: 'MAIN SURVEILLANCE',
      items: [
        { label: 'Surveillance Hub', href: '/dashboard', icon: Activity },
        { label: 'Investigations', href: '/investigations', icon: Layers },
        { label: 'Evidence Player', href: '/evidence', icon: Video },
      ]
    },
    {
      title: 'AI FORENSIC TOOLS',
      items: [
        { label: 'Forensic Search', href: '/search', icon: Search },
        { label: 'Forensic Reports', href: '/reports', icon: FileText },
      ]
    }
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#080b12] border-r border-white/10 text-slate-200">
      {/* Brand Header */}
      <div className="p-5 border-b border-white/10">
        <a href="/dashboard" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00e5ff] via-[#0284c7] to-[#9333ea] flex items-center justify-center p-[1px] shadow-[0_0_15px_rgba(0,229,255,0.4)] shrink-0">
            <div className="w-full h-full bg-[#07090e] rounded-[11px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-[#00e5ff] group-hover:scale-110 transition-transform duration-300" />
            </div>
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold tracking-wider text-base text-white font-mono">
                VISION<span className="text-[#00e5ff]">TRACE</span>
              </span>
              <span className="px-1 py-0.5 rounded text-[9px] font-bold tracking-widest bg-[#00e5ff]/10 text-[#00e5ff] border border-[#00e5ff]/30">
                AI
              </span>
            </div>
            <p className="text-[9px] tracking-tight text-slate-400 font-mono truncate">
              FORENSIC SURVEILLANCE
            </p>
          </div>
        </a>
      </div>

      {/* Primary CTA Button */}
      <div className="p-4 border-b border-white/5">
        <a
          href="/investigations/new"
          className="w-full py-2.5 px-3 rounded-xl font-bold text-xs tracking-wider bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_18px_rgba(0,229,255,0.35)] transition-all flex items-center justify-center space-x-2"
        >
          <PlusCircle className="w-4 h-4 shrink-0" />
          <span>NEW INVESTIGATION</span>
        </a>
      </div>

      {/* Navigation Links Grouped */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navGroups.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            <div className="px-3 text-[10px] font-mono font-semibold tracking-wider text-slate-500 uppercase">
              {group.title}
            </div>
            <div className="space-y-1 pt-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive =
                  pathname === item.href ||
                  (item.href !== '/dashboard' && pathname.startsWith(item.href));
                return (
                  <a
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                      isActive
                        ? 'bg-[#00e5ff]/15 text-[#00e5ff] border border-[#00e5ff]/35 shadow-[0_0_15px_rgba(0,229,255,0.15)] font-semibold'
                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-[#00e5ff]' : 'text-slate-400 group-hover:text-slate-200'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-[#00e5ff]" />}
                  </a>
                );
              })}
            </div>
          </div>
        ))}

        {/* Demo Mode Quick Action */}
        <div className="px-2 pt-2">
          <div className="p-3 rounded-xl bg-purple-950/30 border border-purple-500/25 space-y-2">
            <div className="flex items-center space-x-1.5 text-xs font-mono font-bold text-purple-300">
              <Sparkles className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
              <span>Viva Showcase</span>
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              Pre-load complete multi-camera heist case with masked POI and gait kinematics.
            </p>
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="w-full py-1.5 px-2.5 rounded-lg text-xs font-semibold bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 transition-colors"
            >
              {seeding ? 'Loading Demo...' : 'Load Viva Demo Case'}
            </button>
          </div>
        </div>
      </div>

      {/* System Status & Engine Info (Footer of Sidebar) */}
      <div className="p-4 border-t border-white/10 bg-[#06080d] space-y-2 font-mono text-[11px]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-emerald-400 font-semibold tracking-wider text-[10px]">
              GRID ACTIVE
            </span>
          </div>
          <span className="text-[9px] text-[#00e5ff] bg-[#00e5ff]/10 px-1.5 py-0.5 rounded border border-[#00e5ff]/20">
            PRO v1.0
          </span>
        </div>

        <div className="text-[10px] text-slate-400 truncate">
          {time || '2026-09-08 19:35:00 UTC'}
        </div>

        <div className="text-[9px] text-slate-500 pt-1 border-t border-white/5 truncate">
          YOLOv8 • MediaPipe Pose • ByteTrack
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside className="hidden md:flex flex-col w-64 fixed inset-y-0 left-0 z-40 no-print">
        {sidebarContent}
      </aside>

      {/* Mobile Top Header with Hamburger */}
      <div className="md:hidden flex items-center justify-between p-4 bg-[#080b12] border-b border-white/10 sticky top-0 z-50 no-print">
        <a href="/dashboard" className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-[#00e5ff]/15 border border-[#00e5ff]/30 flex items-center justify-center text-[#00e5ff]">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="font-extrabold text-sm text-white font-mono">
            VISION<span className="text-[#00e5ff]">TRACE AI</span>
          </span>
        </a>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg bg-white/5 text-slate-300 border border-white/10"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex no-print">
          <div className="w-72 h-full">
            {sidebarContent}
          </div>
          <div className="flex-1" onClick={() => setMobileOpen(false)} />
        </div>
      )}
    </>
  );
}
