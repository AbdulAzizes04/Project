"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  BookOpen, CheckCircle, Clock, ArrowUpRight,
  AlertCircle, Calendar, Sparkles, Flame, CheckCircle2
} from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { EmptyState } from "@/components/common/EmptyState";

interface RoadmapItem {
  week: number;
  skill_id: number | null;
  skill_name: string;
  title: string;
  resource_url: string | null;
  estimated_hours: number;
  gap_status: string;
  learning_priority: string;
  status: string;
  progress_percent: number;
}

const PRIORITY_CARD_STYLE: Record<string, string> = {
  HIGH: "border-rose-200/90 bg-rose-50/10",
  MEDIUM: "border-amber-200/90 bg-amber-50/10",
  LOW: "border-emerald-200/90 bg-emerald-50/10",
};

const PRIORITY_BADGE: Record<string, string> = {
  HIGH: "bg-rose-50 text-rose-700 border-rose-200",
  MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
  LOW: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

export default function RoadmapPage() {
  const [roadmapData, setRoadmapData] = useState<{ career_name: string; roadmap: RoadmapItem[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data: any = await api.skillGap.getRoadmap();
        if (data.success) setRoadmapData(data);
        else setError(data.message || "No roadmap available.");
      } catch (e: any) {
        setError(e.message);
      }
      setLoading(false);
    })();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center h-64 items-center w-full">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !roadmapData) {
    return (
      <div className="w-full space-y-6">
        <PageHeader
          eyebrow="CURRICULUM SYNTHESIS"
          title="Learning Roadmap"
          subtitle="Adaptive, weekly skill acquisition plan formulated to close your identified skill gaps."
        />
        <EmptyState
          icon={AlertCircle}
          title="No Roadmap Available"
          description={error || "Generate career recommendations first, then your personalized learning roadmap will appear here."}
          primaryAction={{
            label: "Go to Recommendations",
            href: "/dashboard/recommendations",
            icon: Sparkles,
          }}
        />
      </div>
    );
  }

  const weeks = Array.from(new Set(roadmapData.roadmap.map((r) => r.week))).sort((a, b) => a - b);
  const totalHours = roadmapData.roadmap.reduce((s, r) => s + r.estimated_hours, 0);
  const highPriorityCount = roadmapData.roadmap.filter((r) => r.learning_priority === "HIGH").length;

  return (
    <div className="w-full space-y-6">
      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="CURRICULUM SYNTHESIS"
        title="Learning Roadmap"
        subtitle={`Personalized skill-building curriculum formulated for ${roadmapData.career_name}`}
      />

      {/* 2. MAIN ROADMAP + SIDE SUMMARY: grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr) */}
      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)] gap-5 w-full items-start">
        {/* Left: Main Roadmap Timeline */}
        <div className="space-y-6 min-w-0">
          <div className="relative py-1">
            {/* Vertical spine line */}
            <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-slate-200" />

            <div className="space-y-6">
              {weeks.map((week) => {
                const items = roadmapData.roadmap.filter((r) => r.week === week);
                return (
                  <div key={week} className="relative pl-14">
                    {/* Week Indicator Badge */}
                    <div className="absolute left-0 top-3 w-12 flex items-center justify-center">
                      <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xs font-black shadow-xs ring-4 ring-white">
                        W{week}
                      </div>
                    </div>

                    {/* Learning Items for this week */}
                    <div className="space-y-3">
                      {items.map((item, i) => (
                        <div
                          key={i}
                          className={`bg-white rounded-xl p-5 border shadow-xs hover:shadow-md transition-all duration-200 ${
                            PRIORITY_CARD_STYLE[item.learning_priority] || "border-slate-200/90"
                          }`}
                        >
                          <div className="flex items-start gap-3.5">
                            <div
                              className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                                item.status === "COMPLETED"
                                  ? "bg-emerald-50 text-emerald-600 border border-emerald-200"
                                  : "bg-slate-50 text-slate-400 border border-slate-200"
                              }`}
                            >
                              {item.status === "COMPLETED" ? (
                                <CheckCircle className="w-4 h-4 text-emerald-600" />
                              ) : (
                                <Clock className="w-4 h-4 text-slate-500" />
                              )}
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="font-bold text-slate-900 text-sm">
                                  {item.skill_name}
                                </h3>
                                <span
                                  className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${
                                    PRIORITY_BADGE[item.learning_priority] || "bg-slate-50 text-slate-600 border-slate-200"
                                  }`}
                                >
                                  {item.learning_priority} PRIORITY
                                </span>
                                <span className="text-[11px] text-slate-400 font-medium">
                                  ~{item.estimated_hours}h estimated
                                </span>
                              </div>

                              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                                {item.title}
                              </p>

                              {item.resource_url && (
                                <a
                                  href={item.resource_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 mt-2.5 transition-colors"
                                >
                                  <span>Explore Learning Resource</span>
                                  <ArrowUpRight className="w-3.5 h-3.5" />
                                </a>
                              )}
                            </div>

                            {item.progress_percent > 0 && (
                              <div className="text-right shrink-0">
                                <span className="text-xs font-extrabold text-indigo-600">
                                  {item.progress_percent}%
                                </span>
                                <div className="w-16 h-1.5 bg-slate-100 rounded-full mt-1.5 overflow-hidden">
                                  <div
                                    className="h-full bg-indigo-600 rounded-full"
                                    style={{ width: `${item.progress_percent}%` }}
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Side Summary Card */}
        <div className="space-y-4 min-w-0">
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-5">
            <div>
              <h3 className="text-base font-bold text-slate-900">Curriculum Overview</h3>
              <p className="text-xs text-slate-500 mt-0.5">Summary metrics for {roadmapData.career_name}</p>
            </div>

            <div className="space-y-3">
              <StatCard
                label="Total Duration"
                value={`${weeks.length} Weeks`}
                description="Sequential milestone cadence"
                icon={Calendar}
                colorScheme="indigo"
              />
              <StatCard
                label="Est. Study Hours"
                value={`${totalHours} Hours`}
                description="Self-paced project & course hours"
                icon={Clock}
                colorScheme="amber"
              />
              <StatCard
                label="High Priority Items"
                value={highPriorityCount}
                description="Foundational prerequisites"
                icon={Flame}
                colorScheme="violet"
              />
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-600 space-y-1.5">
              <span className="font-bold text-slate-800 block">Milestone Advisory:</span>
              <p className="leading-relaxed text-[11px] text-slate-500">
                Weekly goals adapt sequentially. Focus first on HIGH priority foundations before progressing to project synthesis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
