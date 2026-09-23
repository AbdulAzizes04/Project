"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  BookOpen, CheckCircle2, Clock, Plus, Filter,
  TrendingUp, X, Sparkles
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

import { PageHeader } from "@/components/common/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { EmptyState } from "@/components/common/EmptyState";

const ITEM_TYPES = ["COURSE", "PROJECT", "CERTIFICATION", "SKILL"];
const STATUSES = ["NOT_STARTED", "IN_PROGRESS", "COMPLETED"];

export default function LearningProgressPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [newItem, setNewItem] = useState({
    item_type: "COURSE",
    title: "",
    week_number: 1,
    notes: ""
  });

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const data: any = await api.progress.getAll();
      setItems(data || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load progress items");
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItem.title) {
      toast.error("Title is required");
      return;
    }
    try {
      await api.progress.add({
        ...newItem,
        week_number: Number(newItem.week_number) || 1
      });
      toast.success("Learning milestone created!");
      setNewItem({ item_type: "COURSE", title: "", week_number: 1, notes: "" });
      setShowAddModal(false);
      fetchProgress();
    } catch (err: any) {
      toast.error(err.message || "Could not add progress item");
    }
  };

  const handleUpdateStatus = async (id: number, status: string, currentPercent: number) => {
    try {
      const newPercent = status === "COMPLETED" ? 100 : (status === "NOT_STARTED" ? 0 : Math.max(currentPercent, 25));
      await api.progress.update(id, {
        status,
        progress_percent: newPercent
      });
      toast.success("Status updated!");
      fetchProgress();
    } catch (err: any) {
      toast.error(err.message || "Update failed");
    }
  };

  const handleUpdatePercent = async (id: number, currentStatus: string, percent: number) => {
    try {
      let newStatus = currentStatus;
      if (percent === 100) newStatus = "COMPLETED";
      else if (percent > 0 && currentStatus === "NOT_STARTED") newStatus = "IN_PROGRESS";
      else if (percent === 0) newStatus = "NOT_STARTED";

      await api.progress.update(id, {
        status: newStatus,
        progress_percent: percent
      });
      setItems(prev => prev.map(item => item.id === id ? { ...item, progress_percent: percent, status: newStatus } : item));
    } catch (err: any) {
      toast.error(err.message || "Failed to update percentage");
    }
  };

  // Stats calculation
  const totalItems = items.length;
  const completedCount = items.filter(i => i.status === "COMPLETED").length;
  const inProgressCount = items.filter(i => i.status === "IN_PROGRESS").length;
  const avgCompletion = totalItems > 0
    ? Math.round(items.reduce((acc, i) => acc + (i.progress_percent || 0), 0) / totalItems)
    : 0;

  const filteredItems = items.filter(i => {
    if (statusFilter === "ALL") return true;
    return i.status === statusFilter;
  });

  // Group by week
  const groupedByWeek: Record<number, any[]> = {};
  filteredItems.forEach(item => {
    const w = item.week_number || 1;
    if (!groupedByWeek[w]) groupedByWeek[w] = [];
    groupedByWeek[w].push(item);
  });
  const sortedWeeks = Object.keys(groupedByWeek).map(Number).sort((a, b) => a - b);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
          <p className="text-slate-500 font-medium text-xs">Loading progress tracker...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      <Toaster position="top-right" />

      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="ACTIVE SKILL ACQUISITION"
        title="Personal Learning Progress"
        subtitle="Track your learning milestones across courses, projects, and certifications."
        actions={
          <button
            type="button"
            onClick={() => setShowAddModal(true)}
            className="btn-primary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2.5 shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Add Learning Goal</span>
          </button>
        }
      />

      {/* 2. PROGRESS STATISTICS: 4 equal cards (desktop 4 cols, tablet 2 cols, mobile 1 col) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        <StatCard
          label="Total Goals"
          value={totalItems}
          description="Curriculum items tracked"
          icon={BookOpen}
          colorScheme="indigo"
        />

        <StatCard
          label="In Progress"
          value={inProgressCount}
          description="Active learning milestones"
          icon={Clock}
          colorScheme="amber"
        />

        <StatCard
          label="Completed"
          value={completedCount}
          description="Verified achievements"
          icon={CheckCircle2}
          colorScheme="emerald"
        />

        <StatCard
          label="Overall Progress"
          value={`${avgCompletion}%`}
          description="Average milestone completion"
          icon={TrendingUp}
          colorScheme="sky"
        />
      </div>

      {/* 3. PROGRESS FILTER & CONTENT */}
      <div className="space-y-4">
        {/* Compact Filter Toolbar */}
        <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <span className="text-xs font-semibold text-slate-500 mr-1 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <span>Filter:</span>
            </span>

            {["ALL", "NOT_STARTED", "IN_PROGRESS", "COMPLETED"].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  statusFilter === status
                    ? "bg-indigo-600 text-white shadow-xs font-semibold"
                    : "bg-white text-slate-600 hover:bg-slate-100/80 border border-slate-200/70"
                }`}
              >
                {status === "ALL" ? "All" : status.replace("_", " ")}
              </button>
            ))}
          </div>

          <span className="text-xs text-slate-400 font-medium hidden sm:inline">
            Showing {filteredItems.length} of {totalItems} goals
          </span>
        </div>

        {/* Learning Goals or Compact Empty State */}
        {filteredItems.length === 0 ? (
          <EmptyState
            icon={BookOpen}
            title="No learning milestones yet"
            description="Add your first learning goal to start tracking progress across verified weekly milestones."
            primaryAction={{
              label: "Create First Goal",
              onClick: () => setShowAddModal(true),
              icon: Plus,
            }}
          />
        ) : (
          <div className="space-y-6">
            {sortedWeeks.map((week) => (
              <div key={week} className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                    Week {week}
                  </span>
                  <div className="h-px flex-1 bg-slate-200/80" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {groupedByWeek[week].map((item) => (
                    <div
                      key={item.id}
                      className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 hover:shadow-md transition-all duration-200 space-y-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                            {item.item_type}
                          </span>
                          <h4 className="text-sm sm:text-base font-bold text-slate-900 leading-snug">
                            {item.title}
                          </h4>
                        </div>

                        <select
                          value={item.status}
                          onChange={(e) =>
                            handleUpdateStatus(item.id, e.target.value, item.progress_percent)
                          }
                          className={`text-xs font-semibold px-2.5 py-1 rounded-lg border cursor-pointer transition-colors ${
                            item.status === "COMPLETED"
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : item.status === "IN_PROGRESS"
                              ? "bg-amber-50 text-amber-700 border-amber-200"
                              : "bg-slate-50 text-slate-600 border-slate-200"
                          }`}
                        >
                          {STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {s.replace("_", " ")}
                            </option>
                          ))}
                        </select>
                      </div>

                      {item.notes && (
                        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                          {item.notes}
                        </p>
                      )}

                      {/* Progress Slider */}
                      <div className="pt-2 border-t border-slate-100 space-y-1.5">
                        <div className="flex justify-between items-center text-xs font-medium">
                          <span className="text-slate-500">Progress</span>
                          <span
                            className={
                              item.progress_percent === 100
                                ? "text-emerald-600 font-bold"
                                : "text-indigo-600 font-semibold"
                            }
                          >
                            {item.progress_percent}%
                          </span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="5"
                          value={item.progress_percent}
                          onChange={(e) =>
                            handleUpdatePercent(
                              item.id,
                              item.status,
                              parseInt(e.target.value) || 0
                            )
                          }
                          className="w-full accent-indigo-600 h-1.5 bg-slate-100 rounded-lg cursor-pointer"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Learning Goal Modal (Clean SaaS style) */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full border border-slate-200 shadow-xl space-y-4 animate-scale-in">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Create Learning Goal</h3>
                <p className="text-xs text-slate-500">Add a milestone to your active curriculum</p>
              </div>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddItem} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Item Type
                </label>
                <select
                  value={newItem.item_type}
                  onChange={(e) => setNewItem({ ...newItem, item_type: e.target.value })}
                  className="input-field w-full text-xs font-medium"
                >
                  {ITEM_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Milestone Title *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Master React Server Components & Streaming"
                  value={newItem.title}
                  onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                  className="input-field w-full text-xs font-medium"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Week
                </label>
                <input
                  type="number"
                  min="1"
                  max="52"
                  value={newItem.week_number}
                  onChange={(e) =>
                    setNewItem({ ...newItem, week_number: parseInt(e.target.value) || 1 })
                  }
                  className="input-field w-full text-xs font-medium"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Notes / Target Outcomes
                </label>
                <textarea
                  rows={3}
                  placeholder="Key concepts to practice, project integration targets, or certification references..."
                  value={newItem.notes}
                  onChange={(e) => setNewItem({ ...newItem, notes: e.target.value })}
                  className="input-field w-full text-xs font-medium resize-none"
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary text-xs px-4 py-2 font-semibold"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-xs px-4 py-2 font-semibold">
                  Create Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
