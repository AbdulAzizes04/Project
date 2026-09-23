"use client";
import { useEffect, useState } from "react";
import { api, getUserName } from "@/lib/api";
import Link from "next/link";
import {
  Code2, Award, FolderGit2, CheckCircle2,
  RefreshCw, ArrowRight, Target, Sparkles
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

import { DashboardHero } from "@/components/dashboard/DashboardHero";
import { StatCard } from "@/components/common/StatCard";
import { SectionHeader } from "@/components/common/SectionHeader";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { ProfileCompleteness } from "@/components/dashboard/ProfileCompleteness";
import { EmptyState } from "@/components/common/EmptyState";

interface Recommendation {
  id: number;
  career_name: string;
  career_description: string;
  compatibility_score: number;
  rank_order: number;
  skill_compatibility: number;
  academic_compatibility: number;
  interest_compatibility: number;
  matching_skills: string[];
  missing_skills: string[];
}

interface ProfileData {
  completion_percentage: number;
  completion_sections: { section: string; completed: boolean; score: number }[];
  skills_count: number;
  certifications_count: number;
  projects_count: number;
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const userName = getUserName() || "Student";

  const fetchData = async () => {
    try {
      const [profileData, recsData]: any = await Promise.all([
        api.student.getProfile(),
        api.recommendations.getAll(),
      ]);
      setProfile(profileData);
      setRecs(recsData.data || []);
    } catch (e: any) {
      toast.error(e.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerateRecs = async () => {
    setGenerating(true);
    try {
      await api.recommendations.generate(true);
      toast.success("AI Recommendations generated successfully!");
      await fetchData();
    } catch (e: any) {
      toast.error(e.message || "Failed to generate recommendations");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] w-full">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
          <p className="text-slate-500 font-medium text-xs">Computing student skill analytics...</p>
        </div>
      </div>
    );
  }

  const completionPct = profile?.completion_percentage || 0;

  return (
    <div className="w-full space-y-5">
      <Toaster position="top-right" />

      {/* 1. HERO / OVERVIEW BANNER (150-180px compact, full width) */}
      <DashboardHero
        studentName={userName.split(" ")[0]}
        onGenerateClick={handleGenerateRecs}
        isGenerating={generating}
      />

      {/* 2. KPI GRID: 4 equal cards (desktop 4 cols, tablet 2 cols, mobile 1 col), gap 16px */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <StatCard
          label="Profile Strength"
          value={`${completionPct.toFixed(0)}%`}
          description={completionPct >= 80 ? "Optimal calibration" : "Incomplete sections"}
          icon={CheckCircle2}
          colorScheme="emerald"
        />

        <StatCard
          label="Technical Skills"
          value={profile?.skills_count || 0}
          description="Standardized competencies"
          icon={Code2}
          colorScheme="indigo"
        />

        <StatCard
          label="Certifications"
          value={profile?.certifications_count || 0}
          description="Verified credentials"
          icon={Award}
          colorScheme="violet"
        />

        <StatCard
          label="Portfolio Projects"
          value={profile?.projects_count || 0}
          description="Technical implementations"
          icon={FolderGit2}
          colorScheme="amber"
        />
      </div>

      {/* 3. MAIN DASHBOARD GRID: minmax(0, 2fr) minmax(320px, 1fr), gap 20px */}
      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)] gap-5 items-start w-full">
        {/* Left Column (Recommended Career Matches) */}
        <div className="space-y-4 min-w-0">
          <SectionHeader
            title="Your Recommended Career Matches"
            subtitle="Ranked by 7-dimension weighted hybrid scoring & ML probabilities"
            action={
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleGenerateRecs}
                  disabled={generating}
                  className="btn-secondary h-8 px-3 text-xs inline-flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3 h-3 text-slate-500 ${generating ? "animate-spin" : ""}`} />
                  <span>Refresh</span>
                </button>

                <Link
                  href="/dashboard/recommendations"
                  className="btn-secondary h-8 px-3 text-xs inline-flex items-center gap-1 text-indigo-700 bg-indigo-50/70 border-indigo-200/80 hover:bg-indigo-100/70"
                >
                  <span>View All</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            }
          />

          {recs.length === 0 ? (
            <EmptyState
              icon={Target}
              title="No career recommendations yet"
              description="Complete your profile to generate personalized career insights evaluated with Explainable AI."
              primaryAction={{
                label: generating ? "Generating..." : "Generate Recommendations",
                onClick: handleGenerateRecs,
                icon: Sparkles,
              }}
              secondaryAction={{
                label: "Complete Profile",
                href: "/dashboard/profile",
              }}
            />
          ) : (
            <div className="space-y-3.5">
              {recs.slice(0, 3).map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  id={rec.id}
                  career_name={rec.career_name}
                  career_description={rec.career_description}
                  compatibility_score={rec.compatibility_score}
                  rank_order={rec.rank_order}
                  skill_compatibility={rec.skill_compatibility}
                  academic_compatibility={rec.academic_compatibility}
                  interest_compatibility={rec.interest_compatibility}
                  matching_skills={rec.matching_skills}
                  missing_skills={rec.missing_skills}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Column (Profile Completeness) */}
        <div className="space-y-4 min-w-0">
          <SectionHeader
            title="Profile Completeness"
            subtitle="Calibration checklist"
          />
          <ProfileCompleteness
            completionPercentage={completionPct}
            sections={profile?.completion_sections || []}
          />
        </div>
      </div>
    </div>
  );
}
