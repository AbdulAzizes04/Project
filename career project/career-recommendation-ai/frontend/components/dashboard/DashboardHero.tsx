import React from "react";
import { Sparkles, ArrowRight, ShieldCheck, UserCheck } from "lucide-react";
import Link from "next/link";

interface DashboardHeroProps {
  studentName?: string;
  onGenerateClick?: () => void;
  isGenerating?: boolean;
}

export function DashboardHero({
  studentName = "Student",
  onGenerateClick,
  isGenerating = false,
}: DashboardHeroProps) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-indigo-100/90 bg-gradient-to-r from-indigo-50/60 via-white to-slate-50 p-6 sm:px-7 sm:py-6 shadow-xs w-full">
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-100/70 text-indigo-700 text-[11px] font-bold tracking-wide uppercase">
            <Sparkles className="w-3 h-3 text-indigo-600" />
            <span>AI-POWERED CAREER INTELLIGENCE</span>
          </div>

          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight leading-snug">
            Welcome back, {studentName}
          </h2>

          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Your personalized career recommendations are continuously evaluated using
            Explainable AI (SHAP &amp; LIME) against your verified skills, projects, and coursework.
          </p>

          <div className="pt-1 flex flex-wrap items-center gap-4 text-xs font-medium text-slate-500">
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Explainable AI Calibrated
            </span>
            <span className="inline-flex items-center gap-1.5">
              <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
              Role Compatibility Engine Active
            </span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={onGenerateClick}
            disabled={isGenerating}
            className="btn-primary inline-flex items-center justify-center gap-2 text-xs font-semibold px-4 py-2.5 shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isGenerating ? "Evaluating..." : "Generate Recommendations"}</span>
          </button>

          <Link
            href="/dashboard/profile"
            className="btn-secondary inline-flex items-center justify-center gap-2 text-xs font-semibold px-4 py-2.5"
          >
            <span>View Profile</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Subtle glow */}
      <div className="absolute right-0 top-0 -mt-6 -mr-6 w-56 h-56 rounded-full bg-indigo-100/30 blur-2xl pointer-events-none" />
    </div>
  );
}
