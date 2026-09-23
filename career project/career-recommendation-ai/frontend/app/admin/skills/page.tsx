"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Code2, Plus, Search, Filter, Sparkles, Tag, Layers
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

export default function AdminSkillsPage() {
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [showAddModal, setShowAddModal] = useState(false);

  const [newSkill, setNewSkill] = useState({
    name: "",
    category: "Programming",
    description: ""
  });

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const data: any = await api.admin.getSkills();
      setSkills(data.skills || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load skills catalog");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkill.name) {
      toast.error("Skill name is required");
      return;
    }
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/admin/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(newSkill)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err?.detail || "Failed to create skill");
      }
      toast.success("Skill added to global catalog!");
      setShowAddModal(false);
      setNewSkill({ name: "", category: "Programming", description: "" });
      fetchSkills();
    } catch (err: any) {
      toast.error(err.message || "Failed to add skill");
    }
  };

  const categories = Array.from(new Set(skills.map(s => s.category).filter(Boolean)));

  const filteredSkills = skills.filter(s => {
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      (s.aliases || []).some((a: string) => a.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory = selectedCategory === "ALL" || s.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin" />
          <p className="text-slate-400 font-medium">Loading skills ontology...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <Toaster position="top-right" toastOptions={{ style: { background: "#1e1e2f", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" } }} />

      {/* Header */}
      <div className="glass-card p-6 border-cyan-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-3">
            <Code2 className="w-3.5 h-3.5" />
            <span>Ontology & Aliases</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Skills Taxonomy Catalog</h1>
          <p className="text-slate-400 text-sm mt-1">Manage normalized skills, classification categories, and normalization aliases.</p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2 px-5 py-2.5 whitespace-nowrap self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Skill</span>
        </button>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-card p-6 max-w-lg w-full border-cyan-500/30 space-y-4 animate-scale-in">
            <div className="flex justify-between items-center border-b border-white/5 pb-3">
              <h3 className="text-lg font-bold text-white">Add New Skill to Catalog</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreateSkill} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Standardized Skill Name *</label>
                <input
                  type="text"
                  placeholder="e.g. PyTorch"
                  value={newSkill.name}
                  onChange={e => setNewSkill({ ...newSkill, name: e.target.value })}
                  className="input-field w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Domain Category</label>
                <input
                  type="text"
                  placeholder="e.g. AI / Machine Learning"
                  value={newSkill.category}
                  onChange={e => setNewSkill({ ...newSkill, category: e.target.value })}
                  className="input-field w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="Open source machine learning framework based on the Torch library..."
                  value={newSkill.description}
                  onChange={e => setNewSkill({ ...newSkill, description: e.target.value })}
                  className="input-field w-full"
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
                  Create Skill
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Filter and Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search skills or aliases..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input-field w-full pl-9"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1">
          <button
            onClick={() => setSelectedCategory("ALL")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedCategory === "ALL" ? "bg-indigo-600 text-white" : "bg-slate-900/60 text-slate-400 hover:text-white"
            }`}
          >
            All Categories ({skills.length})
          </button>
          {categories.map(c => (
            <button
              key={c}
              onClick={() => setSelectedCategory(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                selectedCategory === c ? "bg-indigo-600 text-white" : "bg-slate-900/60 text-slate-400 hover:text-white"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSkills.map(s => (
          <div key={s.id} className="glass-card p-4 hover:border-cyan-500/30 transition-all space-y-2">
            <div className="flex items-start justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                {s.category}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">#{s.id}</span>
            </div>

            <h3 className="text-base font-bold text-white">{s.name}</h3>

            {s.aliases && s.aliases.length > 0 && (
              <div className="pt-2 border-t border-white/5">
                <span className="text-[10px] text-slate-400 block mb-1">Known Aliases:</span>
                <div className="flex flex-wrap gap-1">
                  {s.aliases.map((a: string) => (
                    <span key={a} className="px-2 py-0.5 rounded bg-slate-900/80 text-[10px] font-mono text-slate-300 border border-white/5">
                      {a}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
