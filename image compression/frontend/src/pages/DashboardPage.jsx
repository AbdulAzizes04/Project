import React, { useState, useEffect } from "react";
import { 
  Images, 
  TrendingDown, 
  Activity, 
  Sparkles, 
  Cpu, 
  ArrowRight, 
  FileCheck2,
  Atom
} from "lucide-react";
import StatCard from "../components/StatCard";
import DisclaimerBanner from "../components/DisclaimerBanner";
import { getDashboard, getModelInfo, getResults } from "../services/api";

export default function DashboardPage({ setActiveTab }) {
  const [stats, setStats] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [recentRuns, setRecentRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [dash, info, runs] = await Promise.all([
          getDashboard(),
          getModelInfo(),
          getResults(6),
        ]);
        setStats(dash);
        setModelInfo(info);
        setRecentRuns(runs.results || []);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Hero */}
      <div className="glass-panel p-6 rounded-3xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-3">
            <Atom className="w-3.5 h-3.5 animate-spin-slow" />
            4th-Year B.Tech Final Year Engineering Project
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Quantum-Enhanced Medical Image Compression & Optimization
          </h1>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Investigating parameterized quantum variational circuits (PQC) integrated with deep convolutional autoencoders. High-ratio lossy latent serialization with real binary <code className="text-indigo-300 font-mono">.qmc</code> bitstream compression.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setActiveTab("compress")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all"
            >
              <Cpu className="w-4 h-4" />
              Start New Compression
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setActiveTab("compare")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
            >
              Compare Against JPEG
            </button>
          </div>
        </div>

        {/* Ambient background glow */}
        <div className="absolute -right-20 -top-20 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -right-10 -bottom-20 w-80 h-80 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Metrics Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Images Ingested"
          value={stats?.total_images ?? 0}
          unit="slices"
          subtext={`${stats?.total_runs ?? 0} compression runs recorded`}
          icon={Images}
          color="indigo"
        />
        <StatCard
          title="Avg Storage Reduction"
          value={stats?.avg_storage_reduction ?? 0}
          unit="%"
          subtext="True disk footprint reduction"
          icon={TrendingDown}
          color="emerald"
        />
        <StatCard
          title="Mean PSNR Fidelity"
          value={stats?.avg_psnr ?? 0}
          unit="dB"
          subtext="Peak Signal-to-Noise Ratio"
          icon={Activity}
          color="cyan"
        />
        <StatCard
          title="Mean Structural SSIM"
          value={stats?.avg_ssim ?? 0}
          unit="/ 1.0"
          subtext="Structural feature preservation"
          icon={Sparkles}
          color="purple"
        />
      </div>

      {/* Quantum Model Architecture Info Bar */}
      <div className="glass-card p-5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Atom className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Quantum Engine Status: Operational</h4>
            <p className="text-xs text-slate-400">
              Backend: <span className="text-slate-200 font-mono">{modelInfo?.quantum_device_backend || "PennyLane default.qubit"}</span> | 
              Qubits: <span className="text-indigo-400 font-semibold">{modelInfo?.number_of_qubits || 4} Qubits</span> | 
              Latent Dimension: <span className="text-purple-400 font-semibold">{modelInfo?.latent_dimension || 8}</span>
            </p>
          </div>
        </div>

        <button
          onClick={() => setActiveTab("architecture")}
          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
        >
          View Circuit Topology <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Recent Compression Runs Table */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <FileCheck2 className="w-4 h-4 text-indigo-400" />
            Recent Compression Evaluations
          </h3>
          <button
            onClick={() => setActiveTab("experiments")}
            className="text-xs text-slate-400 hover:text-white"
          >
            View all
          </button>
        </div>

        {recentRuns.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">
            No compression runs recorded yet. Start by compressing an image!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Run ID</th>
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3">Original Size</th>
                  <th className="py-2.5 px-3">Compressed (.qmc)</th>
                  <th className="py-2.5 px-3">Ratio</th>
                  <th className="py-2.5 px-3">Reduction</th>
                  <th className="py-2.5 px-3">PSNR</th>
                  <th className="py-2.5 px-3">SSIM</th>
                  <th className="py-2.5 px-3">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentRuns.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-slate-400">#{r.id}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        r.model_type.includes("QUANTUM")
                          ? "bg-purple-500/10 text-purple-300 border border-purple-500/30"
                          : r.model_type.includes("CLASSICAL")
                          ? "bg-indigo-500/10 text-indigo-300 border border-indigo-500/30"
                          : "bg-slate-700/50 text-slate-300"
                      }`}>
                        {r.model_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono">{r.original_size_bytes} B</td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400 font-semibold">{r.compressed_size_bytes} B</td>
                    <td className="py-2.5 px-3 font-bold text-white">{r.compression_ratio}x</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-semibold">{r.storage_reduction_percent}%</td>
                    <td className="py-2.5 px-3 text-cyan-400 font-semibold">{r.psnr} dB</td>
                    <td className="py-2.5 px-3 font-mono">{r.ssim}</td>
                    <td className="py-2.5 px-3 text-slate-400">{r.inference_time_ms} ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Safety Notice */}
      <DisclaimerBanner text={stats?.disclaimer} />
    </div>
  );
}
