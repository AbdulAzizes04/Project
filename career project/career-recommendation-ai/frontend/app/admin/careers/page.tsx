"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Briefcase, Plus, Edit2, Trash2, CheckCircle2, XCircle,
  Sparkles, DollarSign, GraduationCap, AlertCircle
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

export default function AdminCareersPage() {
  const [careers, setCareers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    difficulty_level: "INTERMEDIATE",
    min_cgpa: 7.0,
    salary_range: "₹8 - 18 LPA"
  });

  useEffect(() => {
    fetchCareers();
  }, []);

  const fetchCareers = async () => {
    setLoading(true);
    try {
      const data: any = await api.admin.getCareers();
      setCareers(data.careers || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load careers");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCareer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) {
      toast.error("Career name is required");
      return;
    }
    const slug = form.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/admin/careers", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...form, slug, is_active: true })
      });
      if (!res.ok) throw new Error("Failed to create career role");
      toast.success("Career role created successfully!");
      setShowAddModal(false);
      setForm({ name: "", slug: "", description: "", difficulty_level: "INTERMEDIATE", min_cgpa: 7.0, salary_range: "₹8 - 18 LPA" });
      fetchCareers();
    } catch (err: any) {
      toast.error(err.message || "Failed to create career");
    }
  };

  const handleDeactivate = async (id: number) => {
    if (!confirm("Are you sure you want to deactivate this career role?")) return;
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`/api/admin/careers/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to deactivate career role");
      toast.success("Career role status updated");
      fetchCareers();
    } catch (err: any) {
      toast.error(err.message || "Failed to update career");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-violet-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 font-medium">Loading career roles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <Toaster position="top-right" toastOptions={{ style: { background: "#1e1e2f", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" } }} />

      {/* Header */}
      <div className="glass-card p-6 border-violet-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-violet-500/10 text-violet-400 border border-violet-500/20 mb-3">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Career Taxonomy</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Career Role Benchmarks</h1>
          <p className="text-slate-400 text-sm mt-1">Configure target career profiles, eligibility CGPA, and required competencies.</p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2 px-5 py-2.5 whitespace-nowrap self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Career Role</span>
        </button>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-card p-6 max-w-lg w-full border-violet-500/30 space-y-4 animate-scale-in">
            <div className="flex justify-between items-center border-b border-white/5 pb-3">
              <h3 className="text-lg font-bold text-white">Create Career Benchmark</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreateCareer} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Career Title *</label>
                <input
                  type="text"
                  placeholder="e.g. MLOps Engineer"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  className="input-field w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Difficulty Level</label>
                <select
                  value={form.difficulty_level}
                  onChange={e => setForm({ ...form, difficulty_level: e.target.value })}
                  className="input-field w-full"
                >
                  <option value="ENTRY">ENTRY</option>
                  <option value="INTERMEDIATE">INTERMEDIATE</option>
                  <option value="ADVANCED">ADVANCED</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Min CGPA</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    value={form.min_cgpa}
                    onChange={e => setForm({ ...form, min_cgpa: parseFloat(e.target.value) || 0 })}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Salary Range</label>
                  <input
                    type="text"
                    value={form.salary_range}
                    onChange={e => setForm({ ...form, salary_range: e.target.value })}
                    className="input-field w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Role Description</label>
                <textarea
                  rows={3}
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  className="input-field w-full"
                  placeholder="Designs and manages automated machine learning pipelines..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-xs px-5 py-2">
                  Save Role
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Careers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {careers.map(c => (
          <div key={c.id} className="glass-card p-6 flex flex-col justify-between hover:border-violet-500/40 transition-all space-y-4">
            <div>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    c.difficulty_level === "ADVANCED" ? "bg-rose-500/10 text-rose-300 border border-rose-500/20" :
                    c.difficulty_level === "INTERMEDIATE" ? "bg-amber-500/10 text-amber-300 border border-amber-500/20" :
                    "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                  }`}>
                    {c.difficulty_level}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-1.5">{c.name}</h3>
                </div>

                <button
                  onClick={() => handleDeactivate(c.id)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    c.is_active ? "text-emerald-400 hover:text-rose-400" : "text-slate-600 hover:text-emerald-400"
                  }`}
                  title={c.is_active ? "Deactivate role" : "Role is inactive"}
                >
                  {c.is_active ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                </button>
              </div>

              <div className="mt-4 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <GraduationCap className="w-3.5 h-3.5 text-slate-500" /> Min CGPA:
                  </span>
                  <span className="font-bold text-indigo-400">{c.min_cgpa || "None"}</span>
                </div>

                <div className="flex items-center justify-between text-slate-300">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <DollarSign className="w-3.5 h-3.5 text-slate-500" /> Package:
                  </span>
                  <span className="font-bold text-emerald-400">{c.salary_range || "Market Standard"}</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
              <span>{c.required_skills_count || 0} Required Skills</span>
              <span className="text-[11px] text-slate-500">{c.preferred_skills_count || 0} Preferred</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
