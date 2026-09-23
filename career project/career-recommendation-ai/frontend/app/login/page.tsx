"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  Brain, Mail, Lock, Eye, EyeOff, Sparkles, ArrowRight, User,
  CheckCircle2, ShieldCheck, Cpu, Target, Compass
} from "lucide-react";

type Mode = "login" | "register";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [formData, setFormData] = useState({ name: "", email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fillCredentials = (email: string, pass: string, name?: string) => {
    setFormData({ name: name || "", email, password: pass });
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (mode === "register") {
        await api.auth.register({ name: formData.name, email: formData.email, password: formData.password, role: "STUDENT" });
        setSuccess("Account created successfully! Logging you in...");
        const data: any = await api.auth.login({ email: formData.email, password: formData.password });
        router.push("/dashboard");
      } else {
        const data: any = await api.auth.login({ email: formData.email, password: formData.password });
        if (data.role === "ADMIN") {
          router.push("/admin");
        } else {
          router.push("/dashboard");
        }
      }
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please verify and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-white">
      {/* LEFT COLUMN: Premium Branded Showcase */}
      <div className="lg:w-1/2 relative bg-slate-950 p-8 sm:p-12 lg:p-16 flex flex-col justify-between overflow-hidden">
        {/* Subtle Ambient Orbs */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full bg-violet-600/15 blur-[120px] pointer-events-none" />

        {/* Top Brand */}
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-500/20 bg-gradient-to-tr from-indigo-600 to-violet-500">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-black text-white tracking-tight">CareerAI</span>
              <span className="text-[11px] font-bold text-indigo-400 block tracking-widest uppercase">XAI Framework</span>
            </div>
          </div>
        </div>

        {/* Center Pitch */}
        <div className="relative z-10 my-12 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 mb-6">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Dual-Model Explainable AI Architecture</span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-[1.15]">
            Personalized Career Guidance Powered by Transparent AI.
          </h2>

          <p className="text-slate-400 text-base mt-4 leading-relaxed">
            Bridge academic learning and industry expectations with mathematically grounded SHAP and LIME skill analytics, custom gap roadmaps, and peer benchmarks.
          </p>

          {/* Feature List */}
          <div className="mt-8 space-y-4">
            <div className="flex items-start gap-3.5">
              <div className="w-6 h-6 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200">SHAP & LIME Feature Attribution</h4>
                <p className="text-xs text-slate-400 mt-0.5">Understand precisely why each career path was matched with feature-level contributions.</p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-6 h-6 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <Target className="w-4 h-4 text-violet-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200">7-Dimension Compatibility Model</h4>
                <p className="text-xs text-slate-400 mt-0.5">Evaluates academics, technical skills, projects, certifications, aptitude, and interests.</p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <Cpu className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200">98.57% Multi-Class F1 Benchmark</h4>
                <p className="text-xs text-slate-400 mt-0.5">Validated against 5,250 synthetic student cohort profiles across 7 target career roles.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Credential Badge */}
        <div className="relative z-10 pt-6 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            Decision-Support System
          </span>
          <span>B.Tech AI & Data Science Project</span>
        </div>
      </div>

      {/* RIGHT COLUMN: Pristine White Form */}
      <div className="lg:w-1/2 flex items-center justify-center p-6 sm:p-12 lg:p-20 bg-slate-50/40">
        <div className="w-full max-w-md">
          {/* Card Container */}
          <div className="bg-white rounded-3xl p-8 sm:p-10 border border-slate-200 shadow-xl shadow-slate-200/50">
            {/* Header */}
            <div className="mb-8">
              <h3 className="text-2xl font-black text-slate-900 tracking-tight">
                {mode === "login" ? "Sign In to Your Account" : "Create Student Account"}
              </h3>
              <p className="text-slate-500 text-sm mt-1.5">
                {mode === "login"
                  ? "Enter your credentials to access your skill dashboard"
                  : "Join CareerAI to receive personalized career recommendations"}
              </p>
            </div>

            {/* Segmented Mode Selector */}
            <div className="flex p-1 bg-slate-100 rounded-xl mb-6 border border-slate-200/80">
              <button
                type="button"
                onClick={() => { setMode("login"); setError(""); }}
                className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition-all ${
                  mode === "login"
                    ? "bg-white text-indigo-700 shadow-sm border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setMode("register"); setError(""); }}
                className={`flex-1 py-2.5 text-xs font-bold rounded-lg transition-all ${
                  mode === "register"
                    ? "bg-white text-indigo-700 shadow-sm border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Register
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "register" && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Full Name</label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      id="name"
                      type="text"
                      placeholder="e.g. Abdul Aziz"
                      required
                      value={formData.name}
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      className="input-field w-full !pl-11 h-11 text-sm bg-white"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Institutional Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    id="email"
                    type="email"
                    placeholder="student@careerai.edu"
                    required
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                    className="input-field w-full !pl-11 h-11 text-sm bg-white"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-xs font-bold text-slate-700">Password</label>
                  <span className="text-[11px] text-slate-400">Min. 6 characters</span>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    required
                    minLength={6}
                    value={formData.password}
                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                    className="input-field w-full !pl-11 !pr-11 h-11 text-sm bg-white"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors p-1 flex items-center justify-center"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Status alerts */}
              {error && (
                <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                  <span>⚠️</span>
                  <span>{error}</span>
                </div>
              )}

              {success && (
                <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold flex items-center gap-2">
                  <span>✓</span>
                  <span>{success}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                id="submit-btn"
                type="submit"
                disabled={loading}
                className="btn-primary w-full h-11 text-sm font-bold shadow-lg shadow-indigo-500/20 mt-2"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span>{mode === "login" ? "Sign In to Dashboard" : "Complete Registration"}</span>
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Credentials Autofill */}
            <div className="mt-8 pt-6 border-t border-slate-100">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Quick Fill Demo Access</span>
                <span className="text-[10px] text-indigo-600 font-semibold">1-Click Auto-Fill</span>
              </div>
              <div className="grid grid-cols-2 gap-2.5">
                <button
                  type="button"
                  onClick={() => fillCredentials("student@careerai.edu", "Student@123", "Abdul Aziz")}
                  className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-200 transition-all text-left"
                >
                  <div className="text-xs font-bold text-slate-900">Student Account</div>
                  <div className="text-[10px] text-slate-500">student@careerai.edu</div>
                </button>

                <button
                  type="button"
                  onClick={() => fillCredentials("admin@careerai.edu", "Admin@123", "System Administrator")}
                  className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-200 transition-all text-left"
                >
                  <div className="text-xs font-bold text-slate-900">Admin Account</div>
                  <div className="text-[10px] text-slate-500">admin@careerai.edu</div>
                </button>
              </div>
            </div>

            {/* Ethical Disclaimer */}
            <p className="text-center text-[11px] text-slate-400 mt-6 leading-relaxed">
              ⚠️ This system provides career guidance only. It does not guarantee employment outcomes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
