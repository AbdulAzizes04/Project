import React, { useState, useEffect } from "react";
import { History, FileSpreadsheet, Image as ImageIcon, CheckCircle2, TrendingDown } from "lucide-react";
import { getExperiments } from "../services/api";
import DisclaimerBanner from "../components/DisclaimerBanner";

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getExperiments()
      .then((data) => setExperiments(data.experiments || []))
      .catch((err) => console.error("Experiments fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" />
            Experiment Management & Benchmark Logs
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Systematic training logs, loss curves, and evaluation metrics recorded in SQLite database.
          </p>
        </div>

        <a
          href="/media/plots/training_loss_comparison.png"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
        >
          <ImageIcon className="w-4 h-4 text-cyan-400" />
          View Loss Curves
        </a>
      </div>

      {/* Generated Plots Showcase */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3">1. Training Loss & PSNR Convergence</h3>
          <div className="rounded-xl overflow-hidden border border-slate-700/60 bg-black/40">
            <img
              src="/media/plots/training_loss_comparison.png"
              alt="Training Loss Convergence"
              className="w-full h-auto object-contain"
            />
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Compound reconstruction loss (MSE + 0.15 × (1 - SSIM)) across 5 training epochs.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3">2. Comparative Benchmark Metrics</h3>
          <div className="rounded-xl overflow-hidden border border-slate-700/60 bg-black/40">
            <img
              src="/media/plots/model_comparison_metrics.png"
              alt="Model Comparison Metrics"
              className="w-full h-auto object-contain"
            />
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Multi-metric evaluation across JPEG, Classical Autoencoder, and Hybrid Quantum Model.
          </p>
        </div>
      </div>

      {/* Experiments Table */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Logged Experiment Runs (SQLite Table)
          </h3>
          <span className="text-xs text-slate-400">Total: {experiments.length} runs</span>
        </div>

        {experiments.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">
            No training experiments logged yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Run Name</th>
                  <th className="py-2.5 px-3">Model Type</th>
                  <th className="py-2.5 px-3">Dataset</th>
                  <th className="py-2.5 px-3">Epochs</th>
                  <th className="py-2.5 px-3">Qubits</th>
                  <th className="py-2.5 px-3">Latent Dim</th>
                  <th className="py-2.5 px-3">Val PSNR</th>
                  <th className="py-2.5 px-3">Val SSIM</th>
                  <th className="py-2.5 px-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {experiments.map((exp) => (
                  <tr key={exp.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-slate-300">{exp.experiment_name}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        exp.model_type.includes("QUANTUM")
                          ? "bg-purple-500/10 text-purple-300 border border-purple-500/30"
                          : "bg-indigo-500/10 text-indigo-300 border border-indigo-500/30"
                      }`}>
                        {exp.model_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">{exp.dataset}</td>
                    <td className="py-2.5 px-3 font-mono">{exp.epochs}</td>
                    <td className="py-2.5 px-3 font-mono">{exp.num_qubits || "N/A"}</td>
                    <td className="py-2.5 px-3 font-mono">{exp.latent_dim}</td>
                    <td className="py-2.5 px-3 text-cyan-400 font-bold">{exp.avg_psnr} dB</td>
                    <td className="py-2.5 px-3 text-purple-400 font-mono">{exp.avg_ssim}</td>
                    <td className="py-2.5 px-3 text-slate-500">{exp.completed_at?.split(" ")[0]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <DisclaimerBanner />
    </div>
  );
}
