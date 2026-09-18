import React from "react";

export default function StatCard({ title, value, unit = "", subtext, icon: Icon, color = "indigo" }) {
  const colorMap = {
    indigo: {
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
      text: "text-indigo-400",
      glow: "hover:border-indigo-500/40 hover:shadow-indigo-500/10",
    },
    cyan: {
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
      text: "text-cyan-400",
      glow: "hover:border-cyan-500/40 hover:shadow-cyan-500/10",
    },
    emerald: {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      text: "text-emerald-400",
      glow: "hover:border-emerald-500/40 hover:shadow-emerald-500/10",
    },
    purple: {
      bg: "bg-purple-500/10",
      border: "border-purple-500/20",
      text: "text-purple-400",
      glow: "hover:border-purple-500/40 hover:shadow-purple-500/10",
    },
  };

  const current = colorMap[color] || colorMap.indigo;

  return (
    <div
      className={`glass-panel p-5 rounded-2xl border transition-all duration-300 hover:shadow-xl ${current.border} ${current.glow}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl ${current.bg} ${current.text}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold text-white tracking-tight">
          {value}
        </span>
        {unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}
      </div>
      {subtext && (
        <p className="mt-2 text-xs text-slate-400 flex items-center gap-1.5">
          {subtext}
        </p>
      )}
    </div>
  );
}
