import React from "react";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  trend?: string;
  colorScheme?: "indigo" | "emerald" | "amber" | "sky" | "violet";
  className?: string;
}

const colorVariants = {
  indigo: "bg-indigo-50 text-indigo-600 border-indigo-100",
  emerald: "bg-emerald-50 text-emerald-600 border-emerald-100",
  amber: "bg-amber-50 text-amber-600 border-amber-100",
  sky: "bg-sky-50 text-sky-600 border-sky-100",
  violet: "bg-violet-50 text-violet-600 border-violet-100",
};

export function StatCard({
  label,
  value,
  description,
  icon: Icon,
  trend,
  colorScheme = "indigo",
  className = "",
}: StatCardProps) {
  return (
    <div
      className={`h-[132px] p-5 bg-white rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between transition-all duration-200 hover:shadow-md hover:border-slate-300 ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 line-clamp-1">
          {label}
        </span>
        <div
          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border ${colorVariants[colorScheme]}`}
        >
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl sm:text-[28px] font-black tracking-tight text-slate-900 leading-none">
            {value}
          </span>
          {trend && (
            <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              {trend}
            </span>
          )}
        </div>
        {description && (
          <p className="text-xs text-slate-500 mt-1 line-clamp-1 font-medium">
            {description}
          </p>
        )}
      </div>
    </div>
  );
}
