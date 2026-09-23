"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import {
  ArrowRight, Target, TrendingUp, Award, Zap,
  BookOpen, Sparkles, CheckCircle2, AlertCircle, RefreshCw,
  GitCompare, X
} from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";

interface Recommendation {
  id: number;
  career_id: number;
  career_name: string;
  career_description: string;
  career_slug: string;
  compatibility_score: number;
  rank_order: number;
  ml_confidence: number;
  skill_compatibility: number;
  academic_compatibility: number;
  project_compatibility: number;
  certification_compatibility: number;
  aptitude_compatibility: number;
  interest_compatibility: number;
  domain_compatibility: number;
  matching_skills: string[];
  missing_skills: string[];
  generated_at: string;
}

function ExplanationModal({
  recId,
  careerName,
  onClose,
}: {
  recId: number;
  careerName: string;
  onClose: () => void;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"shap" | "lime">("shap");

  useEffect(() => {
    (async () => {
      try {
        const detail: any = await api.recommendations.getDetail(recId);
        setData(detail);
      } catch {}
      setLoading(false);
    })();
  }, [recId]);

  const explanation = data?.explanation;
  const factors = tab === "shap" ? explanation?.top_positive_factors || [] : explanation?.lime_values || [];
  const negFactors = tab === "shap" ? explanation?.top_negative_factors || [] : [];
  const maxVal = Math.max(
    ...factors.map((f: any) => Math.abs(f.shap_value || f.abs_weight || 0)),
    0.001
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white rounded-2xl p-6 max-w-2xl w-full border border-slate-200 shadow-xl space-y-4 animate-scale-in max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Explainable AI Attribution: {careerName}
              </h3>
              <p className="text-xs text-slate-500">SHAP &amp; LIME transparent feature contributions</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : !explanation ? (
          <p className="text-xs text-slate-500 py-6 text-center">No explanation available for this role.</p>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              {(["shap", "lime"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTab(t)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                    tab === t
                      ? "bg-indigo-600 text-white shadow-xs"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
                  }`}
                >
                  {t === "shap" ? "SHAP Global Drivers" : "LIME Local Explanation"}
                </button>
              ))}
            </div>

            <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200/70 text-xs text-amber-900 leading-relaxed font-medium">
              <span className="font-bold">Interpretation:</span> {explanation.human_readable_text}
            </div>

            <div className="grid md:grid-cols-2 gap-5 pt-1">
              <div>
                <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  Positive Contributors
                </p>
                <div className="space-y-2.5">
                  {factors.slice(0, 6).map((f: any, i: number) => {
                    const val = Math.abs(f.shap_value || f.abs_weight || 0);
                    return (
                      <div key={i}>
                        <div className="flex justify-between text-xs mb-1 font-medium">
                          <span className="text-slate-700">{f.label || f.feature_description || f.feature}</span>
                          <span className="text-emerald-700 font-bold">+{(val * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${(val / maxVal) * 100}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {negFactors.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-rose-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                    Areas to Improve
                  </p>
                  <div className="space-y-2.5">
                    {negFactors.slice(0, 6).map((f: any, i: number) => {
                      const val = Math.abs(f.shap_value || f.abs_weight || 0);
                      return (
                        <div key={i}>
                          <div className="flex justify-between text-xs mb-1 font-medium">
                            <span className="text-slate-700">{f.label || f.feature_description || f.feature}</span>
                            <span className="text-rose-600 font-bold">-{(val * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-rose-500 rounded-full transition-all duration-500"
                              style={{ width: `${(val / maxVal) * 100}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex justify-end pt-3 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary text-xs px-4 py-2 font-semibold"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [explainingRec, setExplainingRec] = useState<Recommendation | null>(null);
  const [generating, setGenerating] = useState(false);

  const fetchRecs = async () => {
    const data: any = await api.recommendations.getAll();
    setRecs(data.data || []);
  };

  useEffect(() => {
    (async () => {
      try {
        await fetchRecs();
      } catch {}
      setLoading(false);
    })();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.recommendations.generate(true);
      await fetchRecs();
    } catch {}
    setGenerating(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 w-full">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="EXPLAINABLE AI RECOMMENDATIONS"
        title="Career Matches"
        subtitle="Multi-criteria hybrid AI recommendations with transparent SHAP and LIME feature attributions."
        actions={
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={generating}
              className="btn-primary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2.5 shadow-xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${generating ? "animate-spin" : ""}`} />
              <span>{generating ? "Evaluating..." : "Generate Recommendations"}</span>
            </button>
            <Link
              href="/dashboard/compare"
              className="btn-secondary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2.5"
            >
              <GitCompare className="w-3.5 h-3.5" />
              <span>Compare Careers</span>
            </Link>
          </div>
        }
      />

      {recs.length === 0 ? (
        <EmptyState
          icon={Target}
          title="No career recommendations yet"
          description="Complete your student profile to allow the machine learning classifier and SHAP explainer to calculate career affinities."
          primaryAction={{
            label: generating ? "Generating..." : "Generate Recommendations",
            onClick: handleGenerate,
            icon: Sparkles,
          }}
          secondaryAction={{
            label: "Complete Profile",
            href: "/dashboard/profile",
          }}
        />
      ) : (
        /* 2. CAREER MATCHES GRID: repeat(3, minmax(0, 1fr)) Desktop */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 w-full items-stretch">
          {recs.map((rec) => (
            <div
              key={rec.id}
              className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs hover:border-slate-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                {/* Header: Rank + Title + Score */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1 min-w-0">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider ${
                        rec.rank_order === 1
                          ? "bg-amber-50 text-amber-700 border border-amber-200"
                          : rec.rank_order === 2
                          ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                          : "bg-slate-50 text-slate-700 border border-slate-200"
                      }`}
                    >
                      Rank #{rec.rank_order}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 tracking-tight leading-snug truncate">
                      {rec.career_name}
                    </h3>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="text-2xl font-black text-indigo-600 leading-none">
                      {rec.compatibility_score.toFixed(0)}%
                    </span>
                    <span className="text-[10px] font-bold text-slate-400 uppercase block mt-0.5">
                      Compatibility
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-600 rounded-full transition-all duration-700"
                    style={{ width: `${rec.compatibility_score}%` }}
                  />
                </div>

                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  {rec.career_description}
                </p>

                {/* Matching Skills */}
                <div className="space-y-1.5 pt-1 border-t border-slate-100">
                  <span className="text-[11px] font-semibold text-emerald-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Top Matching Skills:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {rec.matching_skills.slice(0, 3).map((s) => (
                      <span
                        key={s}
                        className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/70"
                      >
                        {s}
                      </span>
                    ))}
                    {rec.matching_skills.length === 0 && (
                      <span className="text-xs text-slate-400">None identified yet</span>
                    )}
                  </div>
                </div>

                {/* Skill Gaps */}
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-semibold text-amber-800 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3 text-amber-600" />
                    Skill Gaps:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {rec.missing_skills.slice(0, 2).map((s) => (
                      <span
                        key={s}
                        className="text-[11px] font-medium text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200/70"
                      >
                        {s}
                      </span>
                    ))}
                    {rec.missing_skills.length === 0 && (
                      <span className="text-xs text-emerald-600 font-semibold">All skills matched!</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setExplainingRec(rec)}
                  className="btn-primary text-xs px-3 py-2 font-semibold flex items-center justify-center gap-1.5"
                >
                  <Zap className="w-3 h-3" />
                  <span>View Explanation</span>
                </button>

                <Link
                  href="/dashboard/compare"
                  className="btn-secondary text-xs px-3 py-2 font-semibold flex items-center justify-center gap-1.5"
                >
                  <GitCompare className="w-3 h-3" />
                  <span>Compare</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SHAP & LIME Explanation Modal */}
      {explainingRec && (
        <ExplanationModal
          recId={explainingRec.id}
          careerName={explainingRec.career_name}
          onClose={() => setExplainingRec(null)}
        />
      )}
    </div>
  );
}
