import React from "react";
import { Atom, LayoutDashboard, Cpu, Layers, History, Info, ShieldAlert } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "compress", label: "Compress & Enhance", icon: Cpu },
    { id: "compare", label: "Model Showdown", icon: Layers },
    { id: "experiments", label: "Experiments", icon: History },
    { id: "architecture", label: "Quantum Design", icon: Atom },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30">
            <Atom className="w-6 h-6 text-white animate-spin-slow" />
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 border-2 border-slate-900 rounded-full animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
                QuantumMedCompress
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                4-Qubit Hybrid
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Scalable Quantum-Enhanced AI Model for Medical Image Optimization
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-900/70 p-1.5 rounded-xl border border-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Safety Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-300 text-xs">
          <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0" />
          <span className="truncate max-w-[200px]" title="Educational/Research project. Not for clinical diagnosis.">
            Academic Research Prototype
          </span>
        </div>
      </div>
    </header>
  );
}
