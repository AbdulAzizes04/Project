"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import {
  Users, Briefcase, Code2, Sparkles, TrendingUp, Cpu,
  CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, Activity
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

export default function AdminOverviewPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data: any = await api.admin.getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load admin analytics");
    } finally {
      setLoading(false);
    }
  };

  const summary = analytics?.summary || {
    total_students: 0,
    total_career_roles: 0,
    total_skills: 0,
    total_recommendations_generated: 0
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-rose-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 font-medium">Loading administrative dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      <Toaster position="top-right" toastOptions={{ style: { background: "#1e1e2f", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" } }} />

      {/* Hero Welcome */}
      <div className="glass-card p-8 border-rose-500/20 relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-linear-to-l from-rose-500/10 to-transparent pointer-events-none" />
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Administrator Control Center</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">System & AI Operations</h1>
          <p className="text-slate-400 text-sm mt-1 max-w-xl">
            Monitor real-time student skill analytics, manage career benchmark profiles, inspect explainable AI pipelines, and oversee recommendation accuracy.
          </p>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-6 border-indigo-500/20 hover:border-indigo-500/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Students</span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-4">{summary.total_students}</div>
          <span className="text-[11px] text-indigo-300 mt-1 block">Active student profiles</span>
        </div>

        <div className="glass-card p-6 border-violet-500/20 hover:border-violet-500/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Career Roles</span>
            <div className="p-2.5 rounded-xl bg-violet-500/10 text-violet-400">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-4">{summary.total_career_roles}</div>
          <span className="text-[11px] text-violet-300 mt-1 block">Configured career benchmarks</span>
        </div>

        <div className="glass-card p-6 border-cyan-500/20 hover:border-cyan-500/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Skills Catalog</span>
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
              <Code2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-4">{summary.total_skills}</div>
          <span className="text-[11px] text-cyan-300 mt-1 block">Standardized tech skills</span>
        </div>

        <div className="glass-card p-6 border-emerald-500/20 hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Recommendations</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white mt-4">{summary.total_recommendations_generated}</div>
          <span className="text-[11px] text-emerald-300 mt-1 block">Inferences generated with XAI</span>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Student Registry</h3>
                <p className="text-xs text-slate-400">Inspect registered students and recommendation statuses</p>
              </div>
            </div>
            <Link href="/admin/students" className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
              <span>View</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-violet-500/10 text-violet-400">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Career Benchmarks</h3>
                <p className="text-xs text-slate-400">Configure career roles, minimum CGPA, and required skill sets</p>
              </div>
            </div>
            <Link href="/admin/careers" className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
              <span>Manage</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">System Analytics</h3>
                <p className="text-xs text-slate-400">Skill gap heatmaps, popular careers, and cohort metrics</p>
              </div>
            </div>
            <Link href="/admin/analytics" className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
              <span>Inspect</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">ML Model Diagnostics</h3>
                <p className="text-xs text-slate-400">Model accuracy (98.6% F1), SHAP KernelExplainer & LIME status</p>
              </div>
            </div>
            <Link href="/admin/model-performance" className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
              <span>Diagnostics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* AI Engine Status Card */}
      <div className="glass-card p-6 border-indigo-500/30">
        <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <span>Explainable AI Engine Pipeline Status</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">Production ML Model</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span>
            </div>
            <p className="text-sm font-bold text-white">Logistic Regression (Multi-class)</p>
            <p className="text-[11px] text-slate-400">F1-Score: 98.57% across 7 career roles</p>
          </div>

          <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">SHAP Engine</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Ready</span>
            </div>
            <p className="text-sm font-bold text-white">KernelExplainer + Heuristic Fallback</p>
            <p className="text-[11px] text-slate-400">Generates Shapley feature importance attributions</p>
          </div>

          <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">LIME Engine</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Ready</span>
            </div>
            <p className="text-sm font-bold text-white">LimeTabularExplainer</p>
            <p className="text-[11px] text-slate-400">Computes local surrogate linear model weights</p>
          </div>
        </div>
      </div>
    </div>
  );
}
