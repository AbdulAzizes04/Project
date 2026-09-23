import React from "react";
import Link from "next/link";
import { ChevronRight, CheckCircle2, AlertCircle } from "lucide-react";

interface RecommendationCardProps {
  id: number;
  career_name: string;
  career_description: string;
  compatibility_score: number;
  rank_order: number;
  skill_compatibility: number;
  academic_compatibility: number;
  interest_compatibility: number;
  matching_skills: string[];
  missing_skills: string[];
}

function ScoreRing({ score, size = 64, strokeWidth = 5 }: { score: number; size?: number; strokeWidth?: number }) {
  const r = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  const color = score >= 75 ? "#10b981" : score >= 50 ? "#6366f1" : "#f59e0b";

  return (
    <div className="relative inline-flex items-center justify-center shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#f1f5f9" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.8s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-xs font-black text-slate-900 leading-none">{score.toFixed(0)}%</span>
        <span className="text-[9px] font-bold text-slate-400 uppercase mt-0.5">Match</span>
      </div>
    </div>
  );
}

export function RecommendationCard({
  id,
  career_name,
  career_description,
  compatibility_score,
  rank_order,
  skill_compatibility,
  academic_compatibility,
  interest_compatibility,
  matching_skills = [],
  missing_skills = [],
}: RecommendationCardProps) {
  const badgeGradient =
    rank_order === 1
      ? "from-amber-500 to-amber-600 text-white shadow-amber-500/20"
      : rank_order === 2
      ? "from-indigo-600 to-indigo-700 text-white shadow-indigo-600/20"
      : "from-slate-700 to-slate-800 text-white shadow-slate-700/20";

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs hover:border-indigo-300 hover:shadow-md transition-all duration-200 space-y-4">
      {/* Header: Rank + Title + Score */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div
            className={`w-8 h-8 rounded-lg bg-gradient-to-br ${badgeGradient} flex items-center justify-center text-xs font-extrabold shadow-sm shrink-0 mt-0.5`}
          >
            #{rank_order}
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight leading-snug">
              {career_name}
            </h3>
            <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed max-w-xl">
              {career_description}
            </p>
          </div>
        </div>

        <ScoreRing score={compatibility_score} size={60} strokeWidth={5} />
      </div>

      {/* Mini 3-dimension breakdown */}
      <div className="grid grid-cols-3 gap-2.5 pt-1 text-xs">
        <div className="bg-slate-50 border border-slate-100/90 rounded-lg p-2 text-center">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Skills</span>
          <span className="text-xs font-black text-indigo-600">{skill_compatibility.toFixed(0)}%</span>
        </div>
        <div className="bg-slate-50 border border-slate-100/90 rounded-lg p-2 text-center">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Academics</span>
          <span className="text-xs font-black text-violet-600">{academic_compatibility.toFixed(0)}%</span>
        </div>
        <div className="bg-slate-50 border border-slate-100/90 rounded-lg p-2 text-center">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Interests</span>
          <span className="text-xs font-black text-emerald-600">{interest_compatibility.toFixed(0)}%</span>
        </div>
      </div>

      {/* Skill matches & gaps pills */}
      <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5 max-w-md">
          {matching_skills.slice(0, 3).map((skill) => (
            <span
              key={skill}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200/60"
            >
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              {skill}
            </span>
          ))}

          {missing_skills.slice(0, 2).map((skill) => (
            <span
              key={skill}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200/60"
            >
              <AlertCircle className="w-3 h-3 text-amber-600" />
              {skill}
            </span>
          ))}

          {matching_skills.length + missing_skills.length > 5 && (
            <span className="text-[11px] text-slate-400 font-medium pl-1">
              +{matching_skills.length + missing_skills.length - 5} more
            </span>
          )}
        </div>

        <Link
          href={`/dashboard/recommendations`}
          className="inline-flex items-center gap-1 text-xs font-bold text-indigo-600 hover:text-indigo-700 hover:underline shrink-0"
        >
          <span>View Explanation</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
