import React, { useState } from "react";
import { 
  Atom, 
  LayoutDashboard, 
  Cpu, 
  Layers, 
  History, 
  ShieldAlert,
  ChevronRight,
  Activity,
  Menu,
  X
} from "lucide-react";

export default function Sidebar({ activeTab, setActiveTab }) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, badge: "Overview" },
    { id: "compress", label: "Compress & Enhance", icon: Cpu, badge: "PQC 4-Qubit" },
    { id: "compare", label: "Model Showdown", icon: Layers, badge: "vs JPEG" },
    { id: "experiments", label: "Experiments", icon: History, badge: "Logs" },
    { id: "architecture", label: "Quantum Design", icon: Atom, badge: "Circuit" },
  ];

  const handleNavClick = (id) => {
    setActiveTab(id);
    setIsMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Top Bar */}
      <div className="md:hidden flex items-center justify-between p-4 glass-panel border-b border-slate-800 sticky top-0 z-40">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
            <Atom className="w-5 h-5 text-white animate-spin-slow" />
          </div>
          <span className="font-bold text-sm text-white">QuantumMedCompress</span>
        </div>
        <button
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
        >
          {isMobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden"
        />
      )}

      {/* Vertical Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-50 h-screen w-72 flex-shrink-0 flex flex-col justify-between glass-panel border-r border-slate-800/90 transition-transform duration-300 ease-in-out ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        } bg-slate-950/95 md:bg-slate-950/80 backdrop-blur-xl`}
      >
        {/* Top Header / Branding */}
        <div className="p-5 border-b border-slate-800/80">
          <div className="flex items-start gap-3">
            <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/30 flex-shrink-0">
              <Atom className="w-6 h-6 text-white animate-spin-slow" />
              <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 border-2 border-slate-950 rounded-full animate-pulse" />
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-base font-bold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
                  QuantumMed
                </span>
                <span className="px-1.5 py-0.5 text-[9px] font-semibold tracking-wider uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                  4-Qubit
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 leading-tight line-clamp-2">
                Medical Image Compression & Optimization
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 py-4 px-3 overflow-y-auto space-y-1.5">
          <div className="px-3 pb-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
            Navigation Menu
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/80"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-transform group-hover:scale-110 ${
                      isActive ? "text-white" : "text-slate-400 group-hover:text-indigo-400"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded-md ${
                      isActive
                        ? "bg-indigo-700/60 text-indigo-100"
                        : "bg-slate-800/80 text-slate-400 group-hover:text-slate-300"
                    }`}
                  >
                    {item.badge}
                  </span>
                  <ChevronRight
                    className={`w-3.5 h-3.5 transition-transform ${
                      isActive
                        ? "text-indigo-200 translate-x-0.5"
                        : "text-slate-600 group-hover:text-slate-400"
                    }`}
                  />
                </div>
              </button>
            );
          })}
        </div>

        {/* Bottom Hardware Status & Disclaimer */}
        <div className="p-4 border-t border-slate-800/80 space-y-3 bg-slate-950/60">
          {/* Quantum Engine Live Status */}
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800/90 flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Activity className="w-4 h-4 animate-pulse" />
            </div>
            <div className="text-[11px] min-w-0">
              <div className="text-white font-medium flex items-center gap-1.5">
                <span>PennyLane Simulator</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <div className="text-slate-400 text-[10px] truncate">
                4 Qubits • Latent Dim 8
              </div>
            </div>
          </div>

          {/* Academic Badge */}
          <div className="flex items-start gap-2 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px]">
            <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-amber-400" />
            <span>Academic Research Prototype • Not for clinical diagnosis</span>
          </div>

          <div className="text-[10px] text-slate-500 text-center font-mono">
            v1.0.0 • B.Tech AI & DS Capstone
          </div>
        </div>
      </aside>
    </>
  );
}
