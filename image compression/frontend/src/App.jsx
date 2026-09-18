import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import DashboardPage from "./pages/DashboardPage";
import CompressPage from "./pages/CompressPage";
import ComparePage from "./pages/ComparePage";
import ExperimentsPage from "./pages/ExperimentsPage";
import ArchitecturePage from "./pages/ArchitecturePage";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row font-sans selection:bg-indigo-500 selection:text-white">
      {/* Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {activeTab === "dashboard" && <DashboardPage setActiveTab={setActiveTab} />}
          {activeTab === "compress" && <CompressPage />}
          {activeTab === "compare" && <ComparePage />}
          {activeTab === "experiments" && <ExperimentsPage />}
          {activeTab === "architecture" && <ArchitecturePage />}
        </main>

        {/* Footer */}
        <footer className="glass-panel border-t border-slate-800/80 py-4 px-6 mt-auto">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
            <div>
              <span className="font-semibold text-slate-300">QuantumMedCompress</span> — 4th-Year B.Tech AI & Data Science Capstone Project
            </div>
            <div className="flex items-center gap-3 text-[11px] text-slate-500">
              <span>PyTorch 2.1.1</span>
              <span>•</span>
              <span>PennyLane 0.44.1</span>
              <span>•</span>
              <span>FastAPI</span>
              <span>•</span>
              <span>React + Tailwind</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
