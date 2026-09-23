"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { GitCompare, X, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";

export default function CompareCareerPage() {
  const [recs, setRecs] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparison, setComparison] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data: any = await api.recommendations.getAll();
        const recsArr = data.data || [];
        setRecs(recsArr);
        if (recsArr.length >= 2) {
          setSelectedIds(recsArr.slice(0, 3).map((r: any) => r.career_id));
        }
      } catch {}
    })();
  }, []);

  useEffect(() => {
    if (selectedIds.length < 2) {
      setComparison([]);
      return;
    }
    (async () => {
      setLoading(true);
      try {
        const data: any = await api.careers.compare(selectedIds);
        setComparison(data.comparison || []);
      } catch {}
      setLoading(false);
    })();
  }, [selectedIds]);

  const toggleId = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 4 ? [...prev, id] : prev
    );
  };

  const COLORS = ["#4f46e5", "#7c3aed", "#059669", "#d97706"];

  return (
    <div className="w-full space-y-6">
      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="MULTIVARIATE EVALUATION"
        title="Career Path Comparison"
        subtitle="Side-by-side benchmark comparing compatibility dimensions, academic matches, and skill coverage."
      />

      {/* 2. CAREER SELECTOR */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">
            Select Roles to Compare (2 to 4 roles)
          </h3>
          <span className="text-xs text-slate-500 font-medium">
            {selectedIds.length} of 4 selected
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {recs.map((r: any) => {
            const selected = selectedIds.includes(r.career_id);
            return (
              <button
                key={r.career_id}
                type="button"
                onClick={() => toggleId(r.career_id)}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  selected
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                {selected && <X className="w-3.5 h-3.5" />}
                <span>{r.career_name}</span>
                <span className="opacity-80">({r.compatibility_score?.toFixed(0)}%)</span>
              </button>
            );
          })}
        </div>
      </div>

      {selectedIds.length < 2 ? (
        <EmptyState
          icon={GitCompare}
          title="Select at least 2 careers to compare"
          description="Choose two or more candidate roles above to generate comparative bar charts and matrix metrics."
        />
      ) : loading ? (
        <div className="flex justify-center h-48 items-center">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : comparison.length > 0 ? (
        <>
          {/* 3. BAR CHART COMPARISON */}
          <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-slate-900">
              Comparative Dimension Breakdown
            </h3>
            <div className="h-72 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparison} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis
                    dataKey="career_name"
                    tick={{ fill: "#475569", fontSize: 12, fontWeight: 500 }}
                    axisLine={{ stroke: "#cbd5e1" }}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    axisLine={{ stroke: "#cbd5e1" }}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#ffffff",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                      fontSize: "12px",
                    }}
                  />
                  {["Compatibility", "Skill Match", "Academic", "Interest"].map((key, i) => (
                    <Bar
                      key={key}
                      dataKey={
                        {
                          Compatibility: "compatibility_score",
                          "Skill Match": "skill_compatibility",
                          Academic: "academic_compatibility",
                          Interest: "interest_compatibility",
                        }[key] || key
                      }
                      fill={COLORS[i]}
                      radius={[4, 4, 0, 0]}
                      name={key}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 4. TABLE COMPARISON */}
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200/80">
                  <tr>
                    <th className="px-6 py-3.5 font-bold uppercase tracking-wider text-slate-500">
                      Evaluation Dimension
                    </th>
                    {comparison.map((c, i) => (
                      <th
                        key={c.career_id}
                        className="px-4 py-3.5 text-center font-bold"
                        style={{ color: COLORS[i] }}
                      >
                        {c.career_name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { label: "Overall Compatibility", key: "compatibility_score" },
                    { label: "Skill Match", key: "skill_compatibility" },
                    { label: "Academic Fit", key: "academic_compatibility" },
                    { label: "Career Interest", key: "interest_compatibility" },
                    { label: "Project Match", key: "project_compatibility" },
                    { label: "Skill Coverage", key: "skill_coverage_percent" },
                    { label: "Skills Matched", key: "strong_skills_count" },
                    { label: "Skills Missing", key: "missing_skills_count" },
                  ].map(({ label, key }) => (
                    <tr key={key} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-3 font-medium text-slate-700">{label}</td>
                      {comparison.map((c) => {
                        const val = c[key];
                        const isPercent =
                          typeof val === "number" &&
                          key !== "strong_skills_count" &&
                          key !== "missing_skills_count";
                        const best = Math.max(...comparison.map((x) => x[key] || 0));
                        const isBest = val === best && val > 0;
                        return (
                          <td key={c.career_id} className="px-4 py-3 text-center">
                            <span
                              className={`font-bold ${
                                isBest ? "text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded" : "text-slate-800"
                              }`}
                            >
                              {val != null ? (isPercent ? `${val.toFixed(0)}%` : val) : "—"}
                              {isBest && isPercent && (
                                <span className="ml-1 text-[10px] text-amber-500">★</span>
                              )}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
