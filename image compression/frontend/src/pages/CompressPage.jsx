import React, { useState } from "react";
import { 
  UploadCloud, 
  Cpu, 
  Download, 
  CheckCircle2, 
  Layers, 
  Atom, 
  RefreshCw,
  Sparkles,
  Zap,
  Flame,
  FileDown
} from "lucide-react";
import ImageCompare from "../components/ImageCompare";
import DisclaimerBanner from "../components/DisclaimerBanner";
import { uploadImage, compressImage } from "../services/api";

export default function CompressPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadedImageId, setUploadedImageId] = useState(null);
  const [modelType, setModelType] = useState("HYBRID_QUANTUM");
  
  // Pipeline status & results
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const stages = [
    { name: "Ingestion & Validation", desc: "Verifies medical image header & grayscale channel" },
    { name: "Preprocessing", desc: "Resizes to 64×64 and normalizes intensities to [0.0, 1.0]" },
    { name: "CNN Encoding", desc: "Hierarchical Conv2D feature extraction into 8D latent vector" },
    { name: "Quantum Circuit", desc: "4-Qubit AngleEmbedding + Variational Rotations + Ring Entanglement" },
    { name: "Binary Serialization", desc: "Quantizes to INT8 & generates on-disk .qmc bitstream" },
    { name: "CNN Reconstruction", desc: "Transposed Conv2D decoding into 64×64 medical slice" },
    { name: "Evaluation Engine", desc: "Calculates exact MSE, PSNR (dB), SSIM, and Storage Reduction" },
  ];

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setUploadedImageId(null);
      setResult(null);
      setErrorMsg(null);
    }
  };

  const handleLoadSample = async () => {
    try {
      setErrorMsg(null);
      // Fetch synthetic slice from static media
      const res = await fetch("/media/synthetic/mri_slice_0001.png");
      const blob = await res.blob();
      const file = new File([blob], "synthetic_mri_slice_0001.png", { type: "image/png" });
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setUploadedImageId(null);
      setResult(null);
    } catch (err) {
      setErrorMsg("Failed to load sample phantom slice: " + err.message);
    }
  };

  const handleRunCompression = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setErrorMsg(null);
    setResult(null);

    try {
      // Stage 1 & 2: Upload
      setCurrentStage(0);
      let imgId = uploadedImageId;
      if (!imgId) {
        const uploadRes = await uploadImage(selectedFile);
        imgId = uploadRes.image_id;
        setUploadedImageId(imgId);
      }

      // Simulate step-by-step visual feedback through stages
      for (let i = 1; i < stages.length - 1; i++) {
        setCurrentStage(i);
        await new Promise((r) => setTimeout(r, 120));
      }

      // Final Stage: Server Compression & Evaluation
      setCurrentStage(stages.length - 1);
      const compRes = await compressImage(imgId, modelType);
      setResult(compRes);
    } catch (err) {
      setErrorMsg(err.message || "Compression pipeline failed");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Engine Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            Medical Image Compression & Quantum Enhancement
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Upload brain MRI, chest X-ray, or CT scan for hybrid quantum-classical optimization.
          </p>
        </div>

        {/* Model Selection Tabs */}
        <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setModelType("HYBRID_QUANTUM")}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg font-medium transition-all ${
              modelType === "HYBRID_QUANTUM"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Atom className="w-3.5 h-3.5" />
            Hybrid Quantum (Proposed)
          </button>
          <button
            onClick={() => setModelType("CLASSICAL_AUTOENCODER")}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg font-medium transition-all ${
              modelType === "CLASSICAL_AUTOENCODER"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            Classical Baseline
          </button>
          <button
            onClick={() => setModelType("JPEG")}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg font-medium transition-all ${
              modelType === "JPEG"
                ? "bg-slate-700 text-white shadow-md"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            JPEG (Q=25)
          </button>
        </div>
      </div>

      {/* Upload and Pipeline Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload Box */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <h3 className="text-sm font-semibold text-white mb-3">1. Select Medical Image</h3>

            {/* Dropzone */}
            <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-6 cursor-pointer bg-slate-900/40 transition-colors">
              <input
                type="file"
                accept=".png,.jpg,.jpeg,.bmp,.tif"
                onChange={handleFileChange}
                className="hidden"
              />
              {previewUrl ? (
                <div className="relative w-40 h-40 rounded-lg overflow-hidden border border-slate-700 bg-black">
                  <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
                </div>
              ) : (
                <div className="flex flex-col items-center text-center">
                  <div className="p-3 rounded-full bg-indigo-500/10 text-indigo-400 mb-2">
                    <UploadCloud className="w-7 h-7" />
                  </div>
                  <span className="text-xs font-semibold text-slate-200">Click or drag image to upload</span>
                  <span className="text-[11px] text-slate-500 mt-1">PNG, JPG, BMP, TIFF (Grayscale preferred)</span>
                </div>
              )}
            </label>

            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-slate-400">Or use benchmark slice:</span>
              <button
                type="button"
                onClick={handleLoadSample}
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
              >
                Load Brain MRI Phantom
              </button>
            </div>

            {/* Action Button */}
            <button
              onClick={handleRunCompression}
              disabled={!selectedFile || isProcessing}
              className={`mt-4 w-full flex items-center justify-center gap-2 py-3 rounded-xl text-xs font-semibold transition-all ${
                !selectedFile || isProcessing
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : modelType === "HYBRID_QUANTUM"
                  ? "bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/30"
                  : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30"
              }`}
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Executing Pipeline ({stages[currentStage]?.name})...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Execute {modelType === "HYBRID_QUANTUM" ? "Quantum Compression" : "Compression"}
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs">
              {errorMsg}
            </div>
          )}
        </div>

        {/* Right Column: Execution Stage Stepper */}
        <div className="lg:col-span-7">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 h-full">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Processing Pipeline Architecture
            </h3>

            <div className="space-y-3">
              {stages.map((stage, idx) => {
                const isPassed = !isProcessing && result && currentStage >= idx;
                const isCurrent = isProcessing && currentStage === idx;
                return (
                  <div
                    key={idx}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-all ${
                      isCurrent
                        ? "bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10"
                        : isPassed
                        ? "bg-slate-900/40 border-slate-800"
                        : "bg-slate-950/30 border-slate-900/60 opacity-60"
                    }`}
                  >
                    <div className="mt-0.5">
                      {isCurrent ? (
                        <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                      ) : isPassed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-600 flex items-center justify-center text-[10px] text-slate-500">
                          {idx + 1}
                        </div>
                      )}
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white flex items-center gap-2">
                        {stage.name}
                        {idx === 3 && modelType === "HYBRID_QUANTUM" && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30">
                            PennyLane 4 Qubits Active
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{stage.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6 pt-2">
          {/* Visual Comparison Inspector */}
          <ImageCompare
            originalUrl={result.original_url}
            reconstructedUrl={result.reconstructed_url}
            heatmapUrl={result.heatmap_url}
            originalSize={result.original_size_bytes}
            compressedSize={result.compressed_size_bytes}
          />

          {/* Metrics Summary Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Storage Reduction</span>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {result.storage_reduction_percent}%
              </div>
              <span className="text-[11px] text-slate-500">Saved disk footprint</span>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Compression Ratio</span>
              <div className="text-2xl font-bold text-white mt-1">
                {result.compression_ratio}x
              </div>
              <span className="text-[11px] text-slate-500">{result.original_size_bytes}B → {result.compressed_size_bytes}B</span>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Fidelity (PSNR)</span>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {result.psnr} dB
              </div>
              <span className="text-[11px] text-slate-500">Peak signal-to-noise</span>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Structural SSIM</span>
              <div className="text-2xl font-bold text-purple-400 mt-1">
                {result.ssim}
              </div>
              <span className="text-[11px] text-slate-500">MSE: {result.mse}</span>
            </div>
          </div>

          {/* Download Artifacts Card */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-semibold text-white">Serialized Binary Package Ready</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Exact bitstream size on disk: <span className="text-emerald-400 font-mono font-semibold">{result.compressed_size_bytes} Bytes</span> (Execution latency: {result.inference_time_ms} ms)
              </p>
            </div>

            <div className="flex items-center gap-2">
              <a
                href={result.compressed_file_url}
                download
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
              >
                <FileDown className="w-4 h-4 text-emerald-400" />
                Download Bitstream ({result.compressed_file_url.endsWith(".qmc") ? ".qmc" : ".jpg"})
              </a>
              <a
                href={result.reconstructed_url}
                download
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all"
              >
                <Download className="w-4 h-4" />
                Download Reconstructed PNG
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Safety Disclaimer */}
      <DisclaimerBanner />
    </div>
  );
}
