"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { getToken, getRole, getUserName, logout } from "@/lib/api";
import {
  Brain, LayoutDashboard, Briefcase, BookOpen, TrendingUp,
  User, Code2, LogOut, Menu, X, ChevronRight,
  Target, BarChart3, Sparkles
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Overview" },
  { href: "/dashboard/recommendations", icon: Target, label: "Career Matches" },
  { href: "/dashboard/skill-gap", icon: BarChart3, label: "Skill Analysis" },
  { href: "/dashboard/roadmap", icon: TrendingUp, label: "Learning Roadmap" },
  { href: "/dashboard/compare", icon: Briefcase, label: "Compare Careers" },
  { href: "/dashboard/profile", icon: User, label: "My Profile" },
  { href: "/dashboard/skills", icon: Code2, label: "Skills & Portfolio" },
  { href: "/dashboard/progress", icon: BookOpen, label: "My Progress" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const token = getToken();
    const role = getRole();
    if (!token) {
      router.replace("/login");
      return;
    }
    if (role === "ADMIN") {
      router.replace("/admin");
      return;
    }
    setUserName(getUserName() || "Student");
  }, [router]);

  const initials = userName
    ? userName.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()
    : "ST";

  // Derive breadcrumb context
  const currentNav = NAV_ITEMS.find(item => 
    item.href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(item.href)
  );
  const pageLabel = currentNav?.label || "Dashboard";

  return (
    <div className="min-h-screen w-full bg-slate-50 font-sans antialiased text-slate-900">
      {/* Mobile Drawer Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar: Truly FIXED to viewport, 260px wide, 100vh height */}
      <aside
        className={`fixed top-0 bottom-0 left-0 w-[260px] h-screen z-40 flex flex-col bg-white border-r border-slate-200/80 transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
      >
        {/* Brand Block: 68px */}
        <div className="h-[68px] flex items-center gap-3 px-6 border-b border-slate-100 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-xs">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <div className="font-extrabold text-slate-900 text-sm tracking-tight leading-none">CareerAI</div>
            <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-wider block mt-1">Explainable AI</span>
          </div>
        </div>

        {/* Navigation: 42px height, 14px padding, 8px radius, 10px gap, 18px icons, 14px text */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3.5 pb-2 pt-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Student Portal
          </div>
          {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
            const isActive = href === "/dashboard" ? pathname === href : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setSidebarOpen(false)}
                className={`h-[42px] flex items-center gap-[10px] px-3.5 rounded-lg text-[14px] font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-50/80 text-indigo-700 font-semibold border border-indigo-100/70"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
                }`}
              >
                <Icon className={`w-[18px] h-[18px] shrink-0 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                <span className="flex-1 truncate">{label}</span>
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-indigo-500 opacity-70" />}
              </Link>
            );
          })}
        </nav>

        {/* User profile & Sign Out: Anchored at the bottom */}
        <div className="p-3 border-t border-slate-100 space-y-2 mt-auto shrink-0 bg-slate-50/50">
          <div className="flex items-center gap-2.5 p-2 rounded-lg bg-white border border-slate-200/80">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-xs shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-900 truncate leading-none">{userName}</p>
              <p className="text-[10px] text-slate-500 font-medium mt-0.5">Student Account</p>
            </div>
          </div>

          <button
            type="button"
            onClick={logout}
            className="flex items-center justify-center gap-2 w-full h-[38px] rounded-lg text-xs font-semibold text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition-colors border border-rose-100/80"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Application Area: Full Remaining Width, with 260px left offset on desktop */}
      <div className="flex min-w-0 flex-1 flex-col min-h-screen lg:pl-[260px]">
        {/* Header: 68px, sticky top-0, 100% width, 0 24px padding */}
        <header className="h-[68px] w-full px-6 flex items-center justify-between border-b border-slate-200/80 bg-white sticky top-0 z-30 shadow-2xs">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="lg:hidden p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              onClick={() => setSidebarOpen(s => !s)}
              aria-label="Toggle menu"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* Breadcrumb Page Context */}
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <span className="text-slate-400">CareerAI</span>
              <span className="text-slate-300">/</span>
              <span className="text-slate-800 font-semibold">{pageLabel}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>AI Engine Active</span>
            </span>

            <div className="h-4 w-px bg-slate-200" />

            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-indigo-100 border border-indigo-200 text-indigo-700 flex items-center justify-center text-xs font-bold">
                {initials}
              </div>
              <span className="hidden sm:inline text-xs font-semibold text-slate-700">
                {userName.split(" ")[0]}
              </span>
            </div>
          </div>
        </header>

        {/* Page Content: Occupies 100% of remaining width without max-width or centering constraints */}
        <main className="min-w-0 flex-1 w-full p-6 lg:px-7 lg:py-6 space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
}
