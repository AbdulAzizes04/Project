"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Users, Search, Filter, CheckCircle2, Clock, Eye,
  BookOpen, Code2, FolderGit2, Award, Sparkles
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

export default function AdminStudentsPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterBatch, setFilterBatch] = useState("ALL");

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const data: any = await api.admin.getStudents();
      setStudents(data.students || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load student registry");
    } finally {
      setLoading(false);
    }
  };

  const batches = Array.from(new Set(students.map(s => s.batch).filter(Boolean)));

  const filteredStudents = students.filter(s => {
    const matchesSearch =
      (s.name || "").toLowerCase().includes(search.toLowerCase()) ||
      (s.email || "").toLowerCase().includes(search.toLowerCase()) ||
      (s.branch || "").toLowerCase().includes(search.toLowerCase());
    const matchesBatch = filterBatch === "ALL" || s.batch === filterBatch;
    return matchesSearch && matchesBatch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-rose-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 font-medium">Loading student cohort...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <Toaster position="top-right" toastOptions={{ style: { background: "#1e1e2f", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" } }} />

      {/* Header */}
      <div className="glass-card p-6 border-rose-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 mb-3">
            <Users className="w-3.5 h-3.5" />
            <span>Cohort Management</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Student Registry</h1>
          <p className="text-slate-400 text-sm mt-1">Review student portfolio completion and recommendation generation status.</p>
        </div>

        <div className="bg-slate-900/60 border border-white/5 px-5 py-3 rounded-xl text-center">
          <span className="text-xs text-slate-400 block">Total Registered</span>
          <span className="text-2xl font-black text-rose-400">{students.length}</span>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by name, email, or branch..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input-field w-full pl-9"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1">
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Batch:
          </span>
          <button
            onClick={() => setFilterBatch("ALL")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterBatch === "ALL" ? "bg-indigo-600 text-white" : "bg-slate-900/60 text-slate-400 hover:text-white"
            }`}
          >
            All Batches
          </button>
          {batches.map(b => (
            <button
              key={b}
              onClick={() => setFilterBatch(b)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                filterBatch === b ? "bg-indigo-600 text-white" : "bg-slate-900/60 text-slate-400 hover:text-white"
              }`}
            >
              Class of {b}
            </button>
          ))}
        </div>
      </div>

      {/* Students Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-slate-900/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-4 px-6">Student</th>
                <th className="py-4 px-6">Branch & Batch</th>
                <th className="py-4 px-6 text-center">Skills</th>
                <th className="py-4 px-6 text-center">Projects</th>
                <th className="py-4 px-6 text-center">Certs</th>
                <th className="py-4 px-6 text-center">AI Rec Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-xs font-medium">
              {filteredStudents.map(s => (
                <tr key={s.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-4 px-6">
                    <div className="font-bold text-white text-sm">{s.name}</div>
                    <div className="text-slate-400 text-[11px]">{s.email}</div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="text-slate-200">{s.branch || "General"}</div>
                    <div className="text-slate-500 text-[11px]">Batch {s.batch || "N/A"}</div>
                  </td>
                  <td className="py-4 px-6 text-center">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20">
                      <Code2 className="w-3 h-3" />
                      {s.skills_count}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-300 font-bold border border-cyan-500/20">
                      <FolderGit2 className="w-3 h-3" />
                      {s.projects_count}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-violet-500/10 text-violet-300 font-bold border border-violet-500/20">
                      <Award className="w-3 h-3" />
                      {s.certifications_count}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center">
                    {s.has_recommendations ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" />
                        Generated
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">
                        <Clock className="w-3 h-3" />
                        Pending
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredStudents.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-10 h-10 text-slate-500 mx-auto mb-2" />
            <p className="text-slate-300 font-semibold">No students match your filter</p>
          </div>
        )}
      </div>
    </div>
  );
}
