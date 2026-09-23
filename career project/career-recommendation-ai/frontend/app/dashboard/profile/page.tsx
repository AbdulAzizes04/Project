"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  User, GraduationCap, Brain, Compass, Save, CheckCircle2,
  Sparkles
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";
import { PageHeader } from "@/components/common/PageHeader";

const DOMAINS_LIST = [
  "Artificial Intelligence", "Machine Learning", "Web Development",
  "Cloud & DevOps", "Cybersecurity", "Data Science", "Mobile Apps",
  "UI/UX Design", "Blockchain", "IoT & Embedded", "Robotics"
];

const CAREERS_LIST = [
  "Data Scientist", "Full Stack Developer", "Cloud / DevOps Engineer",
  "Cybersecurity Analyst", "AI / Machine Learning Engineer",
  "Mobile App Developer", "Product Manager", "Database Administrator"
];

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<"personal" | "academic" | "aptitude" | "interests">("personal");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [completion, setCompletion] = useState<any>(null);

  // Form states
  const [profile, setProfile] = useState({
    name: "",
    phone: "",
    location: "",
    batch: "2024",
    branch: "Computer Science and Engineering",
    bio: "",
  });

  const [academic, setAcademic] = useState({
    tenth_percentage: 85,
    twelfth_percentage: 85,
    cgpa: 8.5,
    semester_scores: { "Sem 1": 8.2, "Sem 2": 8.4, "Sem 3": 8.5, "Sem 4": 8.6, "Sem 5": 8.7, "Sem 6": 8.8 },
    core_subject_performance: { "Data Structures": 88, "Algorithms": 85, "DBMS": 90, "Operating Systems": 82 }
  });

  const [aptitude, setAptitude] = useState({
    quantitative_score: 80,
    logical_reasoning_score: 85,
    verbal_score: 75,
    technical_aptitude_score: 90,
  });

  const [interests, setInterests] = useState<{
    preferred_domains: string[];
    career_interests: string[];
    preferred_technologies: string[];
    soft_skills: Record<string, number>;
  }>({
    preferred_domains: [],
    career_interests: [],
    preferred_technologies: [],
    soft_skills: { "Communication": 4, "Teamwork": 5, "Problem Solving": 5, "Leadership": 4 }
  });

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    setLoading(true);
    try {
      const data: any = await api.student.getProfile();
      if (data) {
        if (data.profile) {
          setProfile({
            name: data.profile.name || "",
            phone: data.profile.phone || "",
            location: data.profile.location || "",
            batch: data.profile.batch || "2024",
            branch: data.profile.branch || "Computer Science and Engineering",
            bio: data.profile.bio || "",
          });
        }
        if (data.academic) {
          setAcademic({
            tenth_percentage: data.academic.tenth_percentage ?? 85,
            twelfth_percentage: data.academic.twelfth_percentage ?? 85,
            cgpa: data.academic.cgpa ?? 8.5,
            semester_scores: data.academic.semester_scores || {},
            core_subject_performance: data.academic.core_subject_performance || {}
          });
        }
        if (data.aptitude) {
          setAptitude({
            quantitative_score: data.aptitude.quantitative_score ?? 80,
            logical_reasoning_score: data.aptitude.logical_reasoning_score ?? 85,
            verbal_score: data.aptitude.verbal_score ?? 75,
            technical_aptitude_score: data.aptitude.technical_aptitude_score ?? 90,
          });
        }
        if (data.interests) {
          setInterests({
            preferred_domains: data.interests.preferred_domains || [],
            career_interests: data.interests.career_interests || [],
            preferred_technologies: data.interests.preferred_technologies || [],
            soft_skills: data.interests.soft_skills || { "Communication": 4, "Teamwork": 5, "Problem Solving": 5, "Leadership": 4 }
          });
        }
        setCompletion({
          percentage: data.completion_percentage || 0,
          sections: data.completion_sections || []
        });
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to load profile data");
    } finally {
      setLoading(false);
    }
  };

  const handleSavePersonal = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.student.updateProfile(profile);
      toast.success("Personal information updated!");
      fetchProfileData();
    } catch (err: any) {
      toast.error(err.message || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAcademic = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.student.updateAcademic(academic);
      toast.success("Academic records updated!");
      fetchProfileData();
    } catch (err: any) {
      toast.error(err.message || "Failed to save academic records");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAptitude = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.student.updateAptitude(aptitude);
      toast.success("Aptitude scores updated!");
      fetchProfileData();
    } catch (err: any) {
      toast.error(err.message || "Failed to save aptitude scores");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveInterests = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.student.updateInterests(interests);
      toast.success("Career interests updated!");
      fetchProfileData();
    } catch (err: any) {
      toast.error(err.message || "Failed to save interests");
    } finally {
      setSaving(false);
    }
  };

  const toggleDomain = (domain: string) => {
    setInterests(prev => ({
      ...prev,
      preferred_domains: prev.preferred_domains.includes(domain)
        ? prev.preferred_domains.filter(d => d !== domain)
        : [...prev.preferred_domains, domain]
    }));
  };

  const toggleCareer = (career: string) => {
    setInterests(prev => ({
      ...prev,
      career_interests: prev.career_interests.includes(career)
        ? prev.career_interests.filter(c => c !== career)
        : [...prev.career_interests, career]
    }));
  };

  const aptitudeTotal = Math.round(
    ((aptitude.quantitative_score + aptitude.logical_reasoning_score + aptitude.verbal_score + aptitude.technical_aptitude_score) / 4)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
          <p className="text-slate-500 font-medium text-xs">Loading student profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      <Toaster position="top-right" />

      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="STUDENT PROFILE MANAGEMENT"
        title="Student Profile & Academic Records"
        subtitle="Keep your verified profile data current to maximize accuracy across recommendation algorithms and SHAP explanations."
      />

      {/* 2. COMPLETION METER BANNER */}
      {completion && (
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative w-14 h-14 shrink-0 flex items-center justify-center">
              <svg className="w-14 h-14 transform -rotate-90">
                <circle cx="28" cy="28" r="22" stroke="#f1f5f9" strokeWidth="5" fill="transparent" />
                <circle
                  cx="28" cy="28" r="22"
                  stroke="#4f46e5"
                  strokeWidth="5"
                  strokeDasharray={`${2 * Math.PI * 22}`}
                  strokeDashoffset={`${2 * Math.PI * 22 * (1 - (completion.percentage || 0) / 100)}`}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700"
                />
              </svg>
              <span className="absolute text-xs font-black text-slate-900">{Math.round(completion.percentage)}%</span>
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Profile Calibration
              </span>
              <p className="text-sm font-bold text-slate-900">
                {completion.percentage >= 80 ? "Comprehensive Calibration" : completion.percentage >= 50 ? "Moderate Completion" : "Incomplete Profile"}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {completion.sections.filter((s: any) => s.completed).length} of {completion.sections.length} sections completed
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Verified for AI Analysis</span>
            </span>
          </div>
        </div>
      )}

      {/* 3. TABS */}
      <div className="flex border-b border-slate-200 gap-2 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab("personal")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "personal"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <User className="w-4 h-4" />
          <span>Personal Info</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("academic")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "academic"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <GraduationCap className="w-4 h-4" />
          <span>Academic Records</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("aptitude")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "aptitude"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Brain className="w-4 h-4" />
          <span>Aptitude Scores</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("interests")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "interests"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>Interests & Domains</span>
        </button>
      </div>

      {/* Tab 1: Personal Info */}
      {activeTab === "personal" && (
        <form onSubmit={handleSavePersonal} className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs space-y-6">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Personal & Contact Information</h2>
            <p className="text-xs text-slate-500 mt-0.5">This profile information is displayed across recommendations.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Full Name</label>
              <input
                type="text"
                value={profile.name}
                onChange={e => setProfile({ ...profile, name: e.target.value })}
                className="input-field w-full text-xs font-medium"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Phone Number</label>
              <input
                type="tel"
                value={profile.phone}
                onChange={e => setProfile({ ...profile, phone: e.target.value })}
                placeholder="+91 9876543210"
                className="input-field w-full text-xs font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Location / City</label>
              <input
                type="text"
                value={profile.location}
                onChange={e => setProfile({ ...profile, location: e.target.value })}
                placeholder="Hyderabad, India"
                className="input-field w-full text-xs font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Graduation Batch</label>
              <select
                value={profile.batch}
                onChange={e => setProfile({ ...profile, batch: e.target.value })}
                className="input-field w-full text-xs font-medium"
              >
                <option value="2023">2023</option>
                <option value="2024">2024</option>
                <option value="2025">2025</option>
                <option value="2026">2026</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Branch / Specialization</label>
              <input
                type="text"
                value={profile.branch}
                onChange={e => setProfile({ ...profile, branch: e.target.value })}
                placeholder="Artificial Intelligence & Data Science"
                className="input-field w-full text-xs font-medium"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Professional Bio / Career Statement</label>
              <textarea
                value={profile.bio}
                onChange={e => setProfile({ ...profile, bio: e.target.value })}
                placeholder="Aspiring AI Engineer with a strong interest in deep learning and distributed systems..."
                rows={4}
                className="input-field w-full text-xs font-medium resize-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-3 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-5 py-2.5 text-xs font-semibold shadow-xs"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? "Saving..." : "Save Personal Info"}</span>
            </button>
          </div>
        </form>
      )}

      {/* Tab 2: Academic Records */}
      {activeTab === "academic" && (
        <form onSubmit={handleSaveAcademic} className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs space-y-6">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Academic Performance Metrics</h2>
            <p className="text-xs text-slate-500 mt-0.5">Academic scores are normalized and fed into compatibility scoring.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">10th Standard (%)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={academic.tenth_percentage}
                onChange={e => setAcademic({ ...academic, tenth_percentage: parseFloat(e.target.value) || 0 })}
                className="input-field w-full text-lg font-bold"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Secondary school score</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">12th Standard / Inter (%)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={academic.twelfth_percentage}
                onChange={e => setAcademic({ ...academic, twelfth_percentage: parseFloat(e.target.value) || 0 })}
                className="input-field w-full text-lg font-bold"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Higher secondary score</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Cumulative GPA (CGPA / 10)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="10"
                value={academic.cgpa}
                onChange={e => setAcademic({ ...academic, cgpa: parseFloat(e.target.value) || 0 })}
                className="input-field w-full text-lg font-bold text-indigo-600"
              />
              <span className="text-[11px] text-slate-500 mt-1 block">College graduation average</span>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Core Computer Science Subjects (Score out of 100)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(academic.core_subject_performance).map(([subj, score]) => (
                <div key={subj} className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-xs text-slate-700 font-semibold mb-1.5 truncate">{subj}</div>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={score}
                      onChange={e => {
                        const val = parseInt(e.target.value) || 0;
                        setAcademic(prev => ({
                          ...prev,
                          core_subject_performance: { ...prev.core_subject_performance, [subj]: val }
                        }));
                      }}
                      className="input-field w-20 text-center font-bold text-xs"
                    />
                    <span className="text-xs text-slate-400 font-medium">/ 100</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end pt-3 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-5 py-2.5 text-xs font-semibold shadow-xs"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? "Saving..." : "Save Academic Records"}</span>
            </button>
          </div>
        </form>
      )}

      {/* Tab 3: Aptitude Scores */}
      {activeTab === "aptitude" && (
        <form onSubmit={handleSaveAptitude} className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900">Aptitude & Analytical Assessment</h2>
              <p className="text-xs text-slate-500 mt-0.5">Evaluates cognitive reasoning, quantitative math, and technical problem solving.</p>
            </div>
            <div className="bg-indigo-50 border border-indigo-200 px-4 py-2 rounded-xl text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 block">Composite Aptitude</span>
              <span className="text-xl font-black text-indigo-700">{aptitudeTotal}%</span>
            </div>
          </div>

          <div className="space-y-4">
            {[
              {
                label: "Quantitative Ability",
                key: "quantitative_score",
                desc: "Mathematical problem solving, statistics, algebra, and numerical reasoning."
              },
              {
                label: "Logical Reasoning",
                key: "logical_reasoning_score",
                desc: "Pattern recognition, deductive logic, and structural analysis."
              },
              {
                label: "Verbal Ability & Comprehension",
                key: "verbal_score",
                desc: "English grammar, sentence comprehension, and verbal reasoning."
              },
              {
                label: "Technical Aptitude & Pseudocode",
                key: "technical_aptitude_score",
                desc: "Code tracing, time complexity analysis, and algorithmic intuition."
              }
            ].map(({ label, key, desc }) => (
              <div key={key} className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
                <div className="flex justify-between items-center text-xs font-semibold text-slate-800">
                  <span>{label}</span>
                  <span className="text-indigo-600 font-bold">{(aptitude as any)[key]}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={(aptitude as any)[key]}
                  onChange={e => setAptitude({ ...aptitude, [key]: parseInt(e.target.value) || 0 })}
                  className="w-full accent-indigo-600 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
                />
                <p className="text-[11px] text-slate-500">{desc}</p>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-3 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-5 py-2.5 text-xs font-semibold shadow-xs"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? "Saving..." : "Save Aptitude Scores"}</span>
            </button>
          </div>
        </form>
      )}

      {/* Tab 4: Interests & Domains */}
      {activeTab === "interests" && (
        <form onSubmit={handleSaveInterests} className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs space-y-6">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Preferred Domains & Career Aspirations</h2>
            <p className="text-xs text-slate-500 mt-0.5">Select the industries and specific career roles you are most passionate about.</p>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Preferred Technical Domains
            </label>
            <div className="flex flex-wrap gap-2">
              {DOMAINS_LIST.map(domain => {
                const isSelected = interests.preferred_domains.includes(domain);
                return (
                  <button
                    type="button"
                    key={domain}
                    onClick={() => toggleDomain(domain)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                      isSelected
                        ? "bg-indigo-600 border-indigo-600 text-white shadow-xs"
                        : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    {isSelected ? "✓ " : "+ "}{domain}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Target Career Roles
            </label>
            <div className="flex flex-wrap gap-2">
              {CAREERS_LIST.map(career => {
                const isSelected = interests.career_interests.includes(career);
                return (
                  <button
                    type="button"
                    key={career}
                    onClick={() => toggleCareer(career)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                      isSelected
                        ? "bg-violet-600 border-violet-600 text-white shadow-xs"
                        : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    {isSelected ? "★ " : ""}{career}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Soft Skills Self-Evaluation (1 to 5 Stars)
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(interests.soft_skills).map(([skill, level]) => (
                <div key={skill} className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80 space-y-1.5">
                  <span className="text-xs font-semibold text-slate-700 block">{skill}</span>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        type="button"
                        key={star}
                        onClick={() => {
                          setInterests(prev => ({
                            ...prev,
                            soft_skills: { ...prev.soft_skills, [skill]: star }
                          }));
                        }}
                        className={`text-base transition-transform hover:scale-125 ${
                          star <= level ? "text-amber-400" : "text-slate-300"
                        }`}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end pt-3 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-5 py-2.5 text-xs font-semibold shadow-xs"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? "Saving..." : "Save Career Interests"}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
