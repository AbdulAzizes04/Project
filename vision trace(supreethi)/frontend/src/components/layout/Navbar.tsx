'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/navigation';
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
  Layers
} from 'lucide-react';
import { seedDemoCase } from '@/lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const [time, setTime] = useState<string>('');
  const [seeding, setSeeding] = useState(false);

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

  const navItems = [
    { label: 'Surveillance Hub', href: '/dashboard', icon: Activity },
    { label: 'Investigations', href: '/investigations', icon: Layers },
    { label: 'Evidence Player', href: '/evidence', icon: Video },
    { label: 'Forensic Search', href: '/search', icon: Search },
    { label: 'Forensic Reports', href: '/reports', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#07090e]/90 backdrop-blur-md no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-6">
          <a href="/dashboard" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00e5ff] via-[#0284c7] to-[#9333ea] flex items-center justify-center p-[1px] shadow-[0_0_15px_rgba(0,229,255,0.4)]">
              <div className="w-full h-full bg-[#07090e] rounded-[7px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-[#00e5ff] group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold tracking-wider text-lg text-white font-mono">
                  VISION<span className="text-[#00e5ff]">TRACE</span>
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold tracking-widest bg-[#00e5ff]/10 text-[#00e5ff] border border-[#00e5ff]/30">
                  AI FORENSICS
                </span>
              </div>
              <p className="text-[10px] tracking-tight text-slate-400 font-mono">
                CRIME SURVEILLANCE & REID PLATFORM
              </p>
            </div>
          </a>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 pl-4 border-l border-white/10">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
              return (
                <a
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-[#00e5ff]/15 text-[#00e5ff] border border-[#00e5ff]/30 shadow-[0_0_12px_rgba(0,229,255,0.15)]'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
        </div>

        {/* Right Info & Actions */}
        <div className="flex items-center space-x-4">
          {/* Status & Clock */}
          <div className="hidden lg:flex flex-col items-end text-right font-mono">
            <div className="flex items-center space-x-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[11px] text-emerald-400 font-semibold tracking-wider">
                GRID ACTIVE
              </span>
            </div>
            <span className="text-[10px] text-slate-400">{time || '2026-09-08 19:30:00 UTC'}</span>
          </div>

          {/* Seed Demo button */}
          <button
            onClick={handleSeed}
            disabled={seeding}
            title="Load realistic demo surveillance case for project viva/showcase"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-purple-950/40 text-purple-300 border border-purple-500/30 hover:bg-purple-900/50 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
            <span>{seeding ? 'Seeding...' : 'Load Viva Demo'}</span>
          </button>

          {/* New Investigation Button */}
          <a
            href="/investigations/new"
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-bold tracking-wide bg-gradient-to-r from-[#00e5ff] to-[#0284c7] text-[#07090e] hover:brightness-110 shadow-[0_0_15px_rgba(0,229,255,0.3)] transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>NEW INVESTIGATION</span>
          </a>
        </div>
      </div>
    </header>
  );
}
