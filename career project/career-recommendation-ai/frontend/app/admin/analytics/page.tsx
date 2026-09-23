"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from "recharts";
import {
  BarChart3, Sparkles, TrendingUp, AlertTriangle, Users, Award
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e"];

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res: any = await api.admin.getAnalytics();
      setData(res);
    } catch (err: any) {
      toast.error(err.message || "Failed to load system analytics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 font-medium">Computing cohort analytics...</p>
        </div>
      </div>
    );
  }

  const popularCareers = data?.popular_careers || [];
  const commonGaps = data?.most_common_skill_gaps || [];
  const skillDist = data?.skill_distribution || [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      <Toaster position="top-right" toastOptions={{ style: { background: "#1e1e2f", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" } }} />

      {/* Header */}
      <div className="glass-card p-6 border-indigo-500/20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Cohort Intelligence</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">System & Skill Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">
          Aggregated cohort skill distribution, institutional curriculum gap identification, and recommendation frequency.
        </p>
      </div>

      {/* Grid of Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Popular Recommended Careers */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Top Recommended Careers</h2>
              <p className="text-xs text-slate-400">Careers most frequently ranked #1 for students</p>
            </div>
            <TrendingUp className="w-5 h-5 text-indigo-400" />
          </div>

          <div className="h-72 w-full pt-4">
            {popularCareers.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={popularCareers} layout="vertical" margin={{ left: 40, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="career_name" stroke="#94a3b8" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="student_count" radius={[0, 4, 4, 0]}>
                    {popularCareers.map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                No recommendations generated yet.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Most Common Institutional Skill Gaps */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Critical Curriculum Skill Gaps</h2>
              <p className="text-xs text-slate-400">Skills most commonly missing across student profiles</p>
            </div>
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>

          <div className="h-72 w-full pt-4">
            {commonGaps.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={commonGaps} layout="vertical" margin={{ left: 40, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="skill_name" stroke="#94a3b8" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="missing_count" fill="#f43f5e" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                No skill gap data recorded.
              </div>
            )}
          </div>
        </div>

        {/* Chart 3: Skill Distribution (Full Width) */}
        <div className="glass-card p-6 space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Student Skill Competency Distribution</h2>
              <p className="text-xs text-slate-400">Number of students possessing each technical skill</p>
            </div>
            <Users className="w-5 h-5 text-cyan-400" />
          </div>

          <div className="h-80 w-full pt-4">
            {skillDist.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillDist} margin={{ bottom: 30, left: 10, right: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis
                    dataKey="skill_name"
                    stroke="#94a3b8"
                    tick={{ fontSize: 10, fill: "#94a3b8" }}
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="student_count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                No skill distribution recorded.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
