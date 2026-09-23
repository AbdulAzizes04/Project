import React from "react";
import Link from "next/link";
import { CheckCircle2, Clock, ArrowRight } from "lucide-react";

interface CompletionSection {
  section: string;
  completed: boolean;
  score: number;
}

interface ProfileCompletenessProps {
  completionPercentage: number;
  sections?: CompletionSection[];
}

export function ProfileCompleteness({
  completionPercentage = 0,
  sections = [],
}: ProfileCompletenessProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 sm:p-6 shadow-xs flex flex-col justify-between space-y-5">
      <div>
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 tracking-tight">
            Profile Completeness
          </h3>
          <span className="text-lg font-black text-indigo-600">
            {completionPercentage.toFixed(0)}%
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          High completeness directly powers higher accuracy in ML classification.
        </p>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-2 mt-4 overflow-hidden">
          <div
            className="bg-indigo-600 h-full rounded-full transition-all duration-700"
            style={{ width: `${Math.min(100, Math.max(0, completionPercentage))}%` }}
          />
        </div>
      </div>

      {/* Checklist (36-40px per item) */}
      <div className="divide-y divide-slate-100">
        {sections.map((section) => (
          <div
            key={section.section}
            className="h-10 flex items-center justify-between text-xs"
          >
            <div className="flex items-center gap-2.5">
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                  section.completed
                    ? "bg-emerald-50 text-emerald-600"
                    : "bg-slate-100 text-slate-400"
                }`}
              >
                {section.completed ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : (
                  <Clock className="w-3.5 h-3.5" />
                )}
              </div>
              <span
                className={`font-medium ${
                  section.completed ? "text-slate-800" : "text-slate-500"
                }`}
              >
                {section.section}
              </span>
            </div>
            <span
              className={`text-[11px] font-bold ${
                section.completed ? "text-emerald-600" : "text-slate-400"
              }`}
            >
              +{section.score}%
            </span>
          </div>
        ))}
      </div>

      {/* Action Button */}
      <Link
        href="/dashboard/profile"
        className="btn-primary w-full text-xs font-semibold py-2.5 flex items-center justify-center gap-2 shadow-xs"
      >
        <span>Complete Profile</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
}
