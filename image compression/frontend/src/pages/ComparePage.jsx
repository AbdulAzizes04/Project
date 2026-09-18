import React, { useState, useEffect } from "react";
import { 
  Layers, 
  BarChart2, 
  Atom, 
  Cpu, 
  TrendingUp, 
  RefreshCw, 
  Check, 
  Zap,
  Flame,
  ArrowUpDown
} from "lucide-react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import DisclaimerBanner from "../components/DisclaimerBanner";
import { uploadImage, compareAll, getBenchmarkData } from "../services/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ComparePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [benchmarkSummary, setBenchmarkSummary] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    // Load pre-computed benchmark dataset if available
    getBenchmarkData()
      .then((res) => {
        if (res.data) setBenchmarkSummary(res.data);
      })
      .catch((err) => console.log("Benchmark fetch:", err));
  }, []);

  const handleLoadSample = async () => {
    try {
      const res = await fetch("/media/synthetic/mri_slice_0005.png");
      const blob = await res.blob();
      const file = new File([blob], "mri_slice_0005.png", { type: "image/png" });
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setComparisonResults(null);
    } catch (err) {
      setErrorMsg("Failed to load sample: " + err.message);
    }
  };

  const handleRunShowdown = async () => {
    if (!selectedFile) return;
    setIsComparing(true);
    setErrorMsg(null);

    try {
      // 1. Upload
      const up = await uploadImage(selectedFile);
      // 2. Compare all
      const res = await compareAll(up.image_id);
      setComparisonResults(res.comparisons);
    } catch (err) {
      setErrorMsg(err.message || "Comparison failed");
    } finally {
      setIsComparing(false);
    }
  };

  // Prepare chart data if results exist
  const chartLabels = comparisonResults
    ? comparisonResults.map((c) => c.model_type.replace("_AUTOENCODER", ""))
    : benchmarkSummary.map((b) => b.model_name);

  const psnrValues = comparisonResults
    ? comparisonResults.map((c) => c.psnr)
    : benchmarkSummary.map((b) => b.psnr);

  const ssimValues = comparisonResults
    ? comparisonResults.map((c) => c.ssim)
    : benchmarkSummary.map((b) => b.ssim);

  const crValues = comparisonResults
    ? comparisonResults.map((c) => c.compression_ratio)
    : benchmarkSummary.map((b) => b.compression_ratio);

  const psnrChartData = {
    labels: chartLabels,
    datasets: [
      {
        label: "PSNR (dB)",
        data: psnrValues,
        backgroundColor: ["rgba(100, 116, 139, 0.7)", "rgba(99, 102, 241, 0.7)", "rgba(168, 85, 247, 0.8)"],
        borderColor: ["#64748b", "#6366f1", "#a855f7"],
        borderWidth: 1.5,
        borderRadius: 8,
      },
    ],
  };

  const crChartData = {
    labels: chartLabels,
    datasets: [
      {
        label: "Compression Ratio (x)",
        data: crValues,
        backgroundColor: ["rgba(100, 116, 139, 0.7)", "rgba(16, 185, 129, 0.7)", "rgba(168, 85, 247, 0.8)"],
        borderColor: ["#64748b", "#10b981", "#a855f7"],
        borderWidth: 1.5,
        borderRadius: 8,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: "rgba(15, 23, 42, 0.9)" },
    },
    scales: {
      x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8", font: { size: 11 } } },
      y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8", font: { size: 11 } } },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            Model Benchmark Showdown
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Controlled head-to-head evaluation: Standard JPEG vs Classical Autoencoder vs Proposed Quantum-Enhanced Model.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleLoadSample}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
          >
            Load Phantom Slice
          </button>
          <button
            onClick={handleRunShowdown}
            disabled={!selectedFile || isComparing}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              !selectedFile || isComparing
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/20"
            }`}
          >
            {isComparing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Executing Showdown...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Run Head-to-Head Comparison
              </>
            )}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs">
          {errorMsg}
        </div>
      )}

      {/* 3-Way Reconstructed Images Grid */}
      {comparisonResults && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {comparisonResults.map((c) => (
            <div key={c.run_id} className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col items-center">
              <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold mb-3 ${
                c.model_type.includes("QUANTUM")
                  ? "bg-purple-500/10 text-purple-300 border border-purple-500/30"
                  : c.model_type.includes("CLASSICAL")
                  ? "bg-indigo-500/10 text-indigo-300 border border-indigo-500/30"
                  : "bg-slate-700/50 text-slate-300"
              }`}>
                {c.model_type}
              </span>

              <div className="w-48 h-48 rounded-xl overflow-hidden bg-black border border-slate-700/80 p-1 mb-3">
                <img
                  src={c.reconstructed_url}
                  alt={c.model_type}
                  className="w-full h-full object-contain rounded-lg"
                />
              </div>

              {/* Mini Stats */}
              <div className="w-full grid grid-cols-2 gap-2 text-center text-xs">
                <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">PSNR</div>
                  <div className="font-bold text-cyan-400">{c.psnr} dB</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">SSIM</div>
                  <div className="font-bold text-purple-400">{c.ssim}</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Size on Disk</div>
                  <div className="font-bold text-emerald-400">{c.compressed_size_bytes} B</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Ratio</div>
                  <div className="font-bold text-white">{c.compression_ratio}x</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Comparative Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            Fidelity Comparison: PSNR (dB)
          </h3>
          <div className="h-56">
            <Bar data={psnrChartData} options={chartOptions} />
          </div>
          <p className="mt-2 text-[11px] text-slate-400 text-center">
            Higher dB reflects closer preservation of spatial intensity values.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            Compression Efficiency: Compression Ratio (x)
          </h3>
          <div className="h-56">
            <Bar data={crChartData} options={chartOptions} />
          </div>
          <p className="mt-2 text-[11px] text-slate-400 text-center">
            True bitstream compression: Latent code quantization + entropy encoding.
          </p>
        </div>
      </div>

      <DisclaimerBanner />
    </div>
  );
}
