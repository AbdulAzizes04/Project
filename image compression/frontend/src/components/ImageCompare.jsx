import React, { useState } from "react";
import { Eye, Layers, Flame, ArrowRightLeft } from "lucide-react";

export default function ImageCompare({ originalUrl, reconstructedUrl, heatmapUrl, originalSize, compressedSize }) {
  const [activeView, setActiveView] = useState("side-by-side"); // "side-by-side", "reconstructed", "heatmap"

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800">
      {/* View Switcher Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">Visual Reconstruction Inspector</h3>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveView("side-by-side")}
            className={`px-3 py-1 rounded-md font-medium transition-all ${
              activeView === "side-by-side"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <ArrowRightLeft className="w-3.5 h-3.5" />
              Side-by-Side
            </span>
          </button>
          <button
            onClick={() => setActiveView("heatmap")}
            className={`px-3 py-1 rounded-md font-medium transition-all ${
              activeView === "heatmap"
                ? "bg-purple-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5" />
              Difference Heatmap
            </span>
          </button>
        </div>
      </div>

      {/* Visual Displays */}
      {activeView === "side-by-side" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Original */}
          <div className="flex flex-col items-center">
            <div className="relative w-full max-w-[280px] aspect-square rounded-xl overflow-hidden border border-slate-700/80 bg-slate-950 p-1">
              <img
                src={originalUrl}
                alt="Original Medical Image"
                className="w-full h-full object-contain rounded-lg"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/70 backdrop-blur-sm text-[11px] font-medium text-slate-300 border border-white/10">
                Original (64×64)
              </span>
            </div>
            <div className="mt-2 text-center text-xs text-slate-400">
              Raw File Size: <span className="text-white font-semibold">{originalSize ? `${originalSize} B` : "4,096 B"}</span>
            </div>
          </div>

          {/* Reconstructed */}
          <div className="flex flex-col items-center">
            <div className="relative w-full max-w-[280px] aspect-square rounded-xl overflow-hidden border border-indigo-500/30 bg-slate-950 p-1 shadow-lg shadow-indigo-500/10">
              <img
                src={reconstructedUrl}
                alt="Reconstructed Medical Image"
                className="w-full h-full object-contain rounded-lg"
              />
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded bg-indigo-950/80 backdrop-blur-sm text-[11px] font-medium text-indigo-300 border border-indigo-500/30">
                Reconstructed
              </span>
            </div>
            <div className="mt-2 text-center text-xs text-slate-400">
              Serialized .qmc Size: <span className="text-emerald-400 font-semibold">{compressedSize ? `${compressedSize} B` : "32 B"}</span>
            </div>
          </div>
        </div>
      )}

      {activeView === "heatmap" && (
        <div className="flex flex-col items-center">
          <div className="relative w-full max-w-[320px] aspect-square rounded-xl overflow-hidden border border-purple-500/30 bg-slate-950 p-1 shadow-lg shadow-purple-500/10">
            <img
              src={heatmapUrl}
              alt="Absolute Error Heatmap"
              className="w-full h-full object-contain rounded-lg"
            />
            <span className="absolute top-2 left-2 px-2 py-0.5 rounded bg-purple-950/80 backdrop-blur-sm text-[11px] font-medium text-purple-300 border border-purple-500/30">
              Distortion Heatmap (Jet Colormap)
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-400 text-center max-w-sm">
            Blue indicates identical pixel intensity (|Original - Reconstructed| ≈ 0); yellow/red highlights focal reconstruction variance.
          </p>
        </div>
      )}
    </div>
  );
}
