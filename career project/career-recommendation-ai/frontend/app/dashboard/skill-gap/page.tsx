"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  CheckCircle2, AlertTriangle, XCircle, BarChart3,
  Sparkles, CheckCircle
} from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { EmptyState } from "@/components/common/EmptyState";

interface GapItem {
  skill_id: number;
  skill_name: string;
  skill_category: string;
  gap_status: "STRONG" | "MODERATE" | "MISSING";
  student_level: string;
  required_level: string;
  learning_priority: string;
  priority_score: number;
}

interface GapData {
  career_id: number;
  career_name: string;
  strong_skills: GapItem[];
  moderate_skills: GapItem[];
  missing_skills: GapItem[];
  skill_coverage_percent: number;
  total_required: number;
  matched_required: number;
}

const PRIORITY_BADGE: Record<string, string> = {
  HIGH: "bg-rose-50 text-rose-700 border-rose-200/80",
  MEDIUM: "bg-amber-50 text-amber-700 border-amber-200/80",
  LOW: "bg-emerald-50 text-emerald-700 border-emerald-200/80",
};

const STATUS_ICON = {
  STRONG: <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />,
  MODERATE: <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />,
  MISSING: <XCircle className="w-4 h-4 text-rose-600 shrink-0" />,
};

function SkillRow({ item }: { item: GapItem }) {
  const pct = { STRONG: 100, MODERATE: 60, MISSING: 0 }[item.gap_status];
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50/70 border border-slate-100 hover:bg-slate-100/60 transition-colors">
      {STATUS_ICON[item.gap_status]}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs sm:text-sm font-semibold text-slate-900 truncate">
            {item.skill_name}
          </span>
          <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-white text-slate-500 border border-slate-200">
            {item.skill_category}
          </span>
        </div>
        <div className="flex items-center gap-2 mt-1.5">
          <div className="flex-1 h-1.5 bg-slate-200/80 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                item.gap_status === "STRONG"
                  ? "bg-emerald-500"
                  : item.gap_status === "MODERATE"
                  ? "bg-amber-500"
                  : "bg-rose-500"
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-500 font-medium shrink-0">
            {item.student_level} → {item.required_level}
          </span>
        </div>
      </div>
      {item.gap_status !== "STRONG" && (
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded border shrink-0 ${
            PRIORITY_BADGE[item.learning_priority] || "bg-slate-100 text-slate-600 border-slate-200"
          }`}
        >
          {item.learning_priority} PRIORITY
        </span>
      )}
    </div>
  );
}

export default function SkillGapPage() {
  const [careers, setCareers] = useState<any[]>([]);
  const [recs, setRecs] = useState<any[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<number | null>(null);
  const [gapData, setGapData] = useState<GapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [gapLoading, setGapLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [careersData, recsData]: any[] = await Promise.all([
          api.careers.getAll(),
          api.recommendations.getAll(),
        ]);
        setCareers(careersData || []);
        const recsArr = recsData.data || [];
        setRecs(recsArr);
        if (recsArr.length > 0) {
          setSelectedCareer(recsArr[0].career_id);
        }
      } catch {}
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (selectedCareer === null) return;
    (async () => {
      setGapLoading(true);
      try {
        const data: any = await api.skillGap.getForCareer(selectedCareer);
        setGapData(data);
      } catch {
        setGapData(null);
      }
      setGapLoading(false);
    })();
  }, [selectedCareer]);

  if (loading) {
    return (
      <div className="flex justify-center h-64 items-center">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const total = gapData
    ? gapData.strong_skills.length + gapData.moderate_skills.length + gapData.missing_skills.length
    : 0;
  const strongPct = total > 0 ? (gapData!.strong_skills.length / total) * 100 : 0;
  const moderatePct = total > 0 ? (gapData!.moderate_skills.length / total) * 100 : 0;
  const missingPct = total > 0 ? (gapData!.missing_skills.length / total) * 100 : 0;

  return (
    <div className="w-full space-y-6">
      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="TARGET ROLE BENCHMARKING"
        title="Skill Gap Analysis"
        subtitle="Identify exact competencies required for your target career and prioritize your active learning focus."
      />

      {/* 2. CAREER SELECTOR TABS */}
      <div className="space-y-2">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Target Career Role
        </span>
        <div className="flex flex-wrap gap-2">
          {recs.map((r: any) => {
            const isSelected = selectedCareer === r.career_id;
            return (
              <button
                key={r.career_id}
                type="button"
                onClick={() => setSelectedCareer(r.career_id)}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isSelected
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200/80"
                }`}
              >
                #{r.rank_order} {r.career_name}
              </button>
            );
          })}
        </div>
      </div>

      {gapLoading ? (
        <div className="flex justify-center h-32 items-center">
          <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : gapData ? (
        <>
          {/* 3. SUMMARY KPI CARDS (4 equal cards) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
            <StatCard
              label="Skill Coverage"
              value={`${gapData.skill_coverage_percent.toFixed(0)}%`}
              description="Aggregate role readiness"
              icon={CheckCircle2}
              colorScheme="indigo"
            />
            <StatCard
              label="Strong Skills"
              value={gapData.strong_skills.length}
              description="Fully satisfied competencies"
              icon={CheckCircle}
              colorScheme="emerald"
            />
            <StatCard
              label="Moderate Skills"
              value={gapData.moderate_skills.length}
              description="Intermediate proficiency"
              icon={AlertTriangle}
              colorScheme="amber"
            />
            <StatCard
              label="Missing Skills"
              value={gapData.missing_skills.length}
              description="Critical learning priorities"
              icon={XCircle}
              colorScheme="violet"
            />
          </div>

          {/* 4. STACKED COVERAGE BAR */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">
                Skill Coverage Breakdown — {gapData.career_name}
              </h3>
              <span className="text-xs font-bold text-indigo-600">
                {gapData.matched_required} of {gapData.total_required} requirements addressed
              </span>
            </div>

            <div className="flex h-3.5 rounded-full overflow-hidden w-full gap-1 bg-slate-100 p-0.5">
              <div
                className="bg-emerald-500 rounded-full transition-all duration-700"
                style={{ width: `${strongPct}%` }}
                title={`Strong: ${strongPct.toFixed(0)}%`}
              />
              <div
                className="bg-amber-500 rounded-full transition-all duration-700"
                style={{ width: `${moderatePct}%` }}
                title={`Moderate: ${moderatePct.toFixed(0)}%`}
              />
              <div
                className="bg-rose-500 rounded-full transition-all duration-700"
                style={{ width: `${missingPct}%` }}
                title={`Missing: ${missingPct.toFixed(0)}%`}
              />
            </div>

            <div className="flex items-center gap-5 pt-1 text-xs font-medium text-slate-600">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                Strong ({gapData.strong_skills.length})
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                Moderate ({gapData.moderate_skills.length})
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                Missing ({gapData.missing_skills.length})
              </span>
            </div>
          </div>

          {/* 5. THREE COLUMN SKILL TABLES */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {[
              {
                title: "Strong Competencies",
                items: gapData.strong_skills,
                badgeColor: "text-emerald-700 bg-emerald-50 border-emerald-200",
              },
              {
                title: "Needs Improvement",
                items: gapData.moderate_skills,
                badgeColor: "text-amber-700 bg-amber-50 border-amber-200",
              },
              {
                title: "Missing Skills",
                items: gapData.missing_skills,
                badgeColor: "text-rose-700 bg-rose-50 border-rose-200",
              },
            ].map(({ title, items, badgeColor }) => (
              <div
                key={title}
                className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-4"
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <h3 className="text-sm font-bold text-slate-900">{title}</h3>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}
                  >
                    {items.length}
                  </span>
                </div>
                <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
                  {items.map((item) => (
                    <SkillRow key={item.skill_id} item={item} />
                  ))}
                  {items.length === 0 && (
                    <p className="text-slate-400 text-xs text-center py-6">
                      No skills in this category
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <EmptyState
          icon={BarChart3}
          title="Generate recommendations first"
          description="Skill gap analysis requires career recommendations to benchmark against your profile."
          primaryAction={{
            label: "Go to Recommendations",
            href: "/dashboard/recommendations",
            icon: Sparkles,
          }}
        />
      )}
    </div>
  );
}
