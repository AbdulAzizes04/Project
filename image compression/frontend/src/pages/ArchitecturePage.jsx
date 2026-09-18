import React from "react";
import { Atom, Cpu, Network, Sparkles, CheckCircle2, ShieldAlert } from "lucide-react";
import DisclaimerBanner from "../components/DisclaimerBanner";

export default function ArchitecturePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-purple-500/20 bg-gradient-to-r from-purple-950/40 via-slate-900/60 to-indigo-950/40">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-3">
          <Atom className="w-3.5 h-3.5" />
          Technical Circuit Specification
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Hybrid Quantum-Classical Neural Architecture
        </h2>
        <p className="mt-2 text-xs md:text-sm text-slate-300 max-w-3xl leading-relaxed">
          The framework synergistically integrates high-capacity Classical Convolutional Autoencoders for spatial feature extraction with a 4-Qubit Parameterized Quantum Circuit (PQC) acting as a non-linear quantum feature enhancer.
        </p>
      </div>

      {/* 4-Qubit Circuit Interactive Diagram */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Network className="w-4 h-4 text-purple-400" />
          Parameterized Quantum Variational Circuit (PQC) Topology
        </h3>

        <div className="bg-slate-950/80 p-5 rounded-xl border border-slate-800 overflow-x-auto font-mono text-xs text-slate-300 space-y-3">
          {/* Wire 0 */}
          <div className="flex items-center gap-2 min-w-[650px]">
            <span className="w-16 font-bold text-purple-400">|q₀⟩ --</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RY(θ₀)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RZ(θ₀)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-purple-900/60 border border-purple-500/40 text-purple-200">Rot(ω₀)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-emerald-900/60 border border-emerald-500/40 text-emerald-200">● (CNOT)</span>
            <span>-----------</span>
            <span className="px-2 py-1 rounded bg-slate-800 border border-slate-600 text-slate-300">⊕</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-cyan-900/60 border border-cyan-500/40 text-cyan-200">⟨Z₀⟩</span>
          </div>

          {/* Wire 1 */}
          <div className="flex items-center gap-2 min-w-[650px]">
            <span className="w-16 font-bold text-purple-400">|q₁⟩ --</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RY(θ₁)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RZ(θ₁)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-purple-900/60 border border-purple-500/40 text-purple-200">Rot(ω₁)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-slate-800 border border-slate-600 text-slate-300">⊕</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-emerald-900/60 border border-emerald-500/40 text-emerald-200">● (CNOT)</span>
            <span>-------</span>
            <span className="px-2 py-1 rounded bg-cyan-900/60 border border-cyan-500/40 text-cyan-200">⟨Z₁⟩</span>
          </div>

          {/* Wire 2 */}
          <div className="flex items-center gap-2 min-w-[650px]">
            <span className="w-16 font-bold text-purple-400">|q₂⟩ --</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RY(θ₂)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RZ(θ₂)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-purple-900/60 border border-purple-500/40 text-purple-200">Rot(ω₂)</span>
            <span>-----------</span>
            <span className="px-2 py-1 rounded bg-slate-800 border border-slate-600 text-slate-300">⊕</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-emerald-900/60 border border-emerald-500/40 text-emerald-200">● (CNOT)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-cyan-900/60 border border-cyan-500/40 text-cyan-200">⟨Z₂⟩</span>
          </div>

          {/* Wire 3 */}
          <div className="flex items-center gap-2 min-w-[650px]">
            <span className="w-16 font-bold text-purple-400">|q₃⟩ --</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RY(θ₃)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-200">RZ(θ₃)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-purple-900/60 border border-purple-500/40 text-purple-200">Rot(ω₃)</span>
            <span>--</span>
            <span className="px-2 py-1 rounded bg-emerald-900/60 border border-emerald-500/40 text-emerald-200">● (CNOT)</span>
            <span>--- (Ring wrap to q₀) ---</span>
            <span className="px-2 py-1 rounded bg-cyan-900/60 border border-cyan-500/40 text-cyan-200">⟨Z₃⟩</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-indigo-300 block mb-1">1. State Preparation</span>
            Maps classical continuous latent features $z$ into Bloch sphere rotation angles $\theta \in [-\pi, \pi]$.
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-purple-300 block mb-1">2. Variational Rotations</span>
            Parameterized single-qubit gates $R_x(\omega_0) R_y(\omega_1) R_z(\omega_2)$ tuned via gradient descent.
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-emerald-300 block mb-1">3. Circular Entanglement</span>
            Closed-ring CNOT topology generates multi-qubit correlations across feature channels.
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-cyan-300 block mb-1">4. Pauli-Z Readout</span>
            Measures expectation values $\langle \sigma_z \rangle \in [-1, 1]$, projected via residual skip connection.
          </div>
        </div>
      </div>

      {/* Classical Backbone Specs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            CNN Encoder Pipeline
          </h4>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Input: Standardized 1-channel grayscale slice (64×64)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Conv1: 1 → 16 channels, LeakyReLU(0.2), MaxPool(2,2) → 32×32</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Conv2: 16 → 32 channels, LeakyReLU(0.2), MaxPool(2,2) → 16×16</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Conv3: 32 → 64 channels, LeakyReLU(0.2), MaxPool(2,2) → 8×8</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Adaptive Pooling & Linear Projection → 8D Latent Vector</span>
            </li>
          </ul>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            CNN Decoder Pipeline
          </h4>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Input: 8D Quantum-Enhanced Latent Vector</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Dense Linear Expansion: 8 → 1024 (reshaped to 64×4×4)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Deconv 1–3: Transposed Conv2D + BatchNorm + LeakyReLU up to 32×32</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Deconv 4: 16 → 1 channel, Sigmoid() output bounded in [0.0, 1.0]</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Loss: Compound MSE + 0.15 × (1 - SSIM)</span>
            </li>
          </ul>
        </div>
      </div>

      <DisclaimerBanner />
    </div>
  );
}
