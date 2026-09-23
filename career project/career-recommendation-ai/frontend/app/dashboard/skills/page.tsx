"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Code2, Award, FolderGit2, Plus, Trash2, ExternalLink,
  Search, Calendar
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";
import { PageHeader } from "@/components/common/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { EmptyState } from "@/components/common/EmptyState";

const PROFICIENCIES = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"];
const COMPLEXITIES = ["BEGINNER", "MEDIUM", "COMPLEX"];

export default function SkillsPortfolioPage() {
  const [activeTab, setActiveTab] = useState<"skills" | "certifications" | "projects">("skills");
  const [loading, setLoading] = useState(true);

  // Skills state
  const [catalog, setCatalog] = useState<any[]>([]);
  const [studentSkills, setStudentSkills] = useState<any[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState<number | "">("");
  const [selectedProficiency, setSelectedProficiency] = useState("INTERMEDIATE");
  const [skillSearch, setSkillSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");

  // Certifications state
  const [certifications, setCertifications] = useState<any[]>([]);
  const [newCert, setNewCert] = useState({
    certification_name: "",
    issuer: "",
    issue_date: "",
    domain: "",
    verification_url: ""
  });
  const [showAddCert, setShowAddCert] = useState(false);

  // Projects state
  const [projects, setProjects] = useState<any[]>([]);
  const [newProject, setNewProject] = useState({
    project_name: "",
    description: "",
    technologies: "",
    domain: "",
    complexity: "MEDIUM",
    role: "Lead Developer",
    duration_months: 3,
    project_url: ""
  });
  const [showAddProject, setShowAddProject] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [skillsData, catalogData, certsData, projectsData]: any = await Promise.all([
        api.portfolio.getSkills(),
        api.portfolio.getSkillsCatalog(),
        api.portfolio.getCertifications(),
        api.portfolio.getProjects()
      ]);
      setStudentSkills(skillsData || []);
      setCatalog(catalogData || []);
      setCertifications(certsData || []);
      setProjects(projectsData || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load portfolio items");
    } finally {
      setLoading(false);
    }
  };

  // Skill Handlers
  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSkillId) {
      toast.error("Please select a skill from the catalog");
      return;
    }
    try {
      await api.portfolio.addSkill({
        skill_id: Number(selectedSkillId),
        proficiency_level: selectedProficiency
      });
      toast.success("Skill added to your profile!");
      setSelectedSkillId("");
      const updated = await api.portfolio.getSkills();
      setStudentSkills(updated as any);
    } catch (err: any) {
      toast.error(err.message || "Could not add skill");
    }
  };

  const handleUpdateProficiency = async (id: number, level: string) => {
    try {
      await api.portfolio.updateSkill(id, { proficiency_level: level });
      toast.success("Proficiency updated!");
      const updated = await api.portfolio.getSkills();
      setStudentSkills(updated as any);
    } catch (err: any) {
      toast.error(err.message || "Could not update proficiency");
    }
  };

  const handleDeleteSkill = async (id: number) => {
    try {
      await api.portfolio.deleteSkill(id);
      toast.success("Skill removed");
      setStudentSkills(prev => prev.filter(s => s.id !== id));
    } catch (err: any) {
      toast.error(err.message || "Failed to remove skill");
    }
  };

  // Cert Handlers
  const handleAddCert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCert.certification_name || !newCert.issuer) {
      toast.error("Certification name and issuer are required");
      return;
    }
    try {
      await api.portfolio.addCertification(newCert);
      toast.success("Certification added!");
      setNewCert({ certification_name: "", issuer: "", issue_date: "", domain: "", verification_url: "" });
      setShowAddCert(false);
      const updated = await api.portfolio.getCertifications();
      setCertifications(updated as any);
    } catch (err: any) {
      toast.error(err.message || "Failed to add certification");
    }
  };

  const handleDeleteCert = async (id: number) => {
    try {
      await api.portfolio.deleteCertification(id);
      toast.success("Certification removed");
      setCertifications(prev => prev.filter(c => c.id !== id));
    } catch (err: any) {
      toast.error(err.message || "Failed to remove certification");
    }
  };

  // Project Handlers
  const handleAddProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProject.project_name) {
      toast.error("Project title is required");
      return;
    }
    try {
      const techArray = newProject.technologies
        ? newProject.technologies.split(",").map(t => t.trim()).filter(Boolean)
        : [];
      await api.portfolio.addProject({
        ...newProject,
        technologies: techArray,
        duration_months: Number(newProject.duration_months) || 1
      });
      toast.success("Project added!");
      setNewProject({
        project_name: "",
        description: "",
        technologies: "",
        domain: "",
        complexity: "MEDIUM",
        role: "Lead Developer",
        duration_months: 3,
        project_url: ""
      });
      setShowAddProject(false);
      const updated = await api.portfolio.getProjects();
      setProjects(updated as any);
    } catch (err: any) {
      toast.error(err.message || "Failed to add project");
    }
  };

  const handleDeleteProject = async (id: number) => {
    try {
      await api.portfolio.deleteProject(id);
      toast.success("Project removed");
      setProjects(prev => prev.filter(p => p.id !== id));
    } catch (err: any) {
      toast.error(err.message || "Failed to remove project");
    }
  };

  const availableCatalog = catalog.filter(c => !studentSkills.some(s => s.skill_id === c.id));
  const categories = Array.from(new Set(studentSkills.map(s => s.skill_category))).filter(Boolean);

  const filteredStudentSkills = studentSkills.filter(s => {
    const matchesSearch = s.skill_name.toLowerCase().includes(skillSearch.toLowerCase());
    const matchesCategory = selectedCategory === "ALL" || s.skill_category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
          <p className="text-slate-500 font-medium text-xs">Loading portfolio items...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Toaster position="top-right" />

      {/* 1. PAGE HEADER */}
      <PageHeader
        eyebrow="TECHNICAL REPERTOIRE"
        title="Skills, Certifications & Projects"
        subtitle="Manage verified technical competencies, industry credentials, and engineering projects."
      />

      {/* 2. STATS ROW (3 equal StatCards) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5">
        <StatCard
          label="Verified Skills"
          value={studentSkills.length}
          description="Standardized technical competencies"
          icon={Code2}
          colorScheme="indigo"
        />
        <StatCard
          label="Industry Credentials"
          value={certifications.length}
          description="External verification links"
          icon={Award}
          colorScheme="violet"
        />
        <StatCard
          label="Technical Projects"
          value={projects.length}
          description="Portfolio implementations"
          icon={FolderGit2}
          colorScheme="amber"
        />
      </div>

      {/* 3. TABS */}
      <div className="flex border-b border-slate-200 gap-2 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab("skills")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "skills"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Code2 className="w-4 h-4" />
          <span>Technical Skills ({studentSkills.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("certifications")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "certifications"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Award className="w-4 h-4" />
          <span>Certifications ({certifications.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("projects")}
          className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs border-b-2 transition-all ${
            activeTab === "projects"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <FolderGit2 className="w-4 h-4" />
          <span>Projects ({projects.length})</span>
        </button>
      </div>

      {/* TAB 1: SKILLS */}
      {activeTab === "skills" && (
        <div className="space-y-5">
          {/* Add Skill Form: minmax(0, 1fr) 220px auto */}
          <form
            onSubmit={handleAddSkill}
            className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_220px_auto] items-end gap-3.5 w-full"
          >
            <div className="w-full min-w-0">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Select Skill from Catalog</label>
              <select
                value={selectedSkillId}
                onChange={e => setSelectedSkillId(e.target.value ? Number(e.target.value) : "")}
                className="input-field w-full text-xs font-medium"
              >
                <option value="">-- Choose a skill ({availableCatalog.length} available) --</option>
                {availableCatalog.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.category})
                  </option>
                ))}
              </select>
            </div>

            <div className="w-full">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Proficiency Level</label>
              <select
                value={selectedProficiency}
                onChange={e => setSelectedProficiency(e.target.value)}
                className="input-field w-full text-xs font-medium"
              >
                {PROFICIENCIES.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="btn-primary w-full md:w-auto flex items-center justify-center gap-2 px-5 py-2.5 text-xs font-semibold shadow-xs"
            >
              <Plus className="w-4 h-4" />
              <span>Add Skill</span>
            </button>
          </form>

          {/* Filter & Search Bar */}
          <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search your skills..."
                value={skillSearch}
                onChange={e => setSkillSearch(e.target.value)}
                className="input-field w-full pl-9 text-xs font-medium h-9"
              />
            </div>

            <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1">
              <button
                type="button"
                onClick={() => setSelectedCategory("ALL")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedCategory === "ALL"
                    ? "bg-indigo-600 text-white font-semibold"
                    : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                All
              </button>
              {categories.map(cat => (
                <button
                  type="button"
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? "bg-indigo-600 text-white font-semibold"
                      : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Student Skills Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredStudentSkills.map(s => (
              <div key={s.id} className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 inline-block mb-1">
                      {s.skill_category}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900">{s.skill_name}</h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDeleteSkill(s.id)}
                    className="text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 transition-colors"
                    title="Remove skill"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium">Proficiency:</span>
                  <select
                    value={s.proficiency_level}
                    onChange={e => handleUpdateProficiency(s.id, e.target.value)}
                    className="bg-slate-50 text-xs font-semibold text-slate-800 border border-slate-200 rounded-lg px-2 py-1 focus:outline-none cursor-pointer"
                  >
                    {PROFICIENCIES.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>

          {filteredStudentSkills.length === 0 && (
            <EmptyState
              icon={Code2}
              title="No skills found"
              description="Use the selection dropdown above to add verified competencies from our standardized catalog."
            />
          )}
        </div>
      )}

      {/* TAB 2: CERTIFICATIONS */}
      {activeTab === "certifications" && (
        <div className="space-y-5">
          <div className="flex justify-between items-center">
            <h2 className="text-base font-bold text-slate-900">Your Certifications</h2>
            <button
              type="button"
              onClick={() => setShowAddCert(!showAddCert)}
              className="btn-primary flex items-center gap-2 text-xs px-3.5 py-2 font-semibold shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{showAddCert ? "Cancel" : "Add Certification"}</span>
            </button>
          </div>

          {/* Add Certification Form */}
          {showAddCert && (
            <form onSubmit={handleAddCert} className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-4 animate-scale-in">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">New Certification Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Certification Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. AWS Certified Solutions Architect"
                    value={newCert.certification_name}
                    onChange={e => setNewCert({ ...newCert, certification_name: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Issuing Organization *</label>
                  <input
                    type="text"
                    placeholder="e.g. Amazon Web Services, Coursera, DeepLearning.AI"
                    value={newCert.issuer}
                    onChange={e => setNewCert({ ...newCert, issuer: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Domain</label>
                  <input
                    type="text"
                    placeholder="e.g. Cloud Computing, AI, Data Science"
                    value={newCert.domain}
                    onChange={e => setNewCert({ ...newCert, domain: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Issue Date</label>
                  <input
                    type="date"
                    value={newCert.issue_date}
                    onChange={e => setNewCert({ ...newCert, issue_date: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Verification URL</label>
                  <input
                    type="url"
                    placeholder="https://coursera.org/verify/..."
                    value={newCert.verification_url}
                    onChange={e => setNewCert({ ...newCert, verification_url: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddCert(false)}
                  className="btn-secondary text-xs px-4 py-2 font-semibold"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-xs px-4 py-2 font-semibold">
                  Save Certification
                </button>
              </div>
            </form>
          )}

          {/* Certifications List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {certifications.map(c => (
              <div key={c.id} className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-lg bg-violet-50 text-violet-600 border border-violet-100 flex items-center justify-center shrink-0">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{c.certification_name}</h3>
                      <p className="text-xs text-slate-500 font-medium">{c.issuer}</p>
                      {c.domain && (
                        <span className="inline-block mt-1.5 px-2 py-0.5 rounded text-[10px] font-semibold bg-violet-50 text-violet-700 border border-violet-100">
                          {c.domain}
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDeleteCert(c.id)}
                    className="text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 transition-colors"
                    title="Delete certification"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <span className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    {c.issue_date ? new Date(c.issue_date).toLocaleDateString() : "No date"}
                  </span>
                  {c.verification_url && (
                    <a
                      href={c.verification_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-700 flex items-center gap-1 font-semibold"
                    >
                      <span>Verify</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>

          {certifications.length === 0 && !showAddCert && (
            <EmptyState
              icon={Award}
              title="No certifications recorded"
              description="Add industry certifications to strengthen your profile matching."
              primaryAction={{
                label: "Add Certification",
                onClick: () => setShowAddCert(true),
                icon: Plus,
              }}
            />
          )}
        </div>
      )}

      {/* TAB 3: PROJECTS */}
      {activeTab === "projects" && (
        <div className="space-y-5">
          <div className="flex justify-between items-center">
            <h2 className="text-base font-bold text-slate-900">Your Technical Projects</h2>
            <button
              type="button"
              onClick={() => setShowAddProject(!showAddProject)}
              className="btn-primary flex items-center gap-2 text-xs px-3.5 py-2 font-semibold shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{showAddProject ? "Cancel" : "Add Project"}</span>
            </button>
          </div>

          {/* Add Project Form */}
          {showAddProject && (
            <form onSubmit={handleAddProject} className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-4 animate-scale-in">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">New Project Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Project Title *</label>
                  <input
                    type="text"
                    placeholder="e.g. Distributed Log Analytics Engine"
                    value={newProject.project_name}
                    onChange={e => setNewProject({ ...newProject, project_name: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Domain</label>
                  <input
                    type="text"
                    placeholder="e.g. Artificial Intelligence, Full Stack"
                    value={newProject.domain}
                    onChange={e => setNewProject({ ...newProject, domain: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Complexity</label>
                  <select
                    value={newProject.complexity}
                    onChange={e => setNewProject({ ...newProject, complexity: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  >
                    {COMPLEXITIES.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Your Role</label>
                  <input
                    type="text"
                    placeholder="e.g. Lead Architect, Backend Developer"
                    value={newProject.role}
                    onChange={e => setNewProject({ ...newProject, role: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Technologies Used (Comma-separated)</label>
                  <input
                    type="text"
                    placeholder="Python, FastAPI, Docker, PyTorch, React"
                    value={newProject.technologies}
                    onChange={e => setNewProject({ ...newProject, technologies: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Description & Architecture</label>
                  <textarea
                    rows={3}
                    placeholder="Brief description of the problem solved, architecture design, and your specific contribution..."
                    value={newProject.description}
                    onChange={e => setNewProject({ ...newProject, description: e.target.value })}
                    className="input-field w-full text-xs font-medium resize-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Duration (Months)</label>
                  <input
                    type="number"
                    min="1"
                    max="36"
                    value={newProject.duration_months}
                    onChange={e => setNewProject({ ...newProject, duration_months: parseInt(e.target.value) || 1 })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Project / Repository URL</label>
                  <input
                    type="url"
                    placeholder="https://github.com/..."
                    value={newProject.project_url}
                    onChange={e => setNewProject({ ...newProject, project_url: e.target.value })}
                    className="input-field w-full text-xs font-medium"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddProject(false)}
                  className="btn-secondary text-xs px-4 py-2 font-semibold"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-xs px-4 py-2 font-semibold">
                  Save Project
                </button>
              </div>
            </form>
          )}

          {/* Projects List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map(p => (
              <div key={p.id} className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all space-y-4">
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          p.complexity === "COMPLEX" ? "bg-rose-50 text-rose-700 border border-rose-200" :
                          p.complexity === "MEDIUM" ? "bg-amber-50 text-amber-700 border border-amber-200" :
                          "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        }`}>
                          {p.complexity}
                        </span>
                        {p.domain && (
                          <span className="text-[11px] text-slate-500 font-medium">in {p.domain}</span>
                        )}
                      </div>
                      <h3 className="text-base font-bold text-slate-900">{p.project_name}</h3>
                      <p className="text-xs text-indigo-600 font-semibold">{p.role}</p>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleDeleteProject(p.id)}
                      className="text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {p.description && (
                    <p className="text-xs text-slate-600 mt-2.5 line-clamp-3 leading-relaxed">
                      {p.description}
                    </p>
                  )}

                  {/* Technologies Tags */}
                  {p.technologies && p.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {p.technologies.map((t: string) => (
                        <span key={t} className="px-2 py-0.5 bg-slate-100 text-[10px] font-mono font-medium text-slate-700 rounded border border-slate-200">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <span>{p.duration_months} month{p.duration_months > 1 ? "s" : ""}</span>
                  {p.project_url && (
                    <a
                      href={p.project_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-700 flex items-center gap-1 font-semibold"
                    >
                      <span>View Project</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>

          {projects.length === 0 && !showAddProject && (
            <EmptyState
              icon={FolderGit2}
              title="No projects recorded"
              description="Add your academic and personal engineering implementations."
              primaryAction={{
                label: "Add Project",
                onClick: () => setShowAddProject(true),
                icon: Plus,
              }}
            />
          )}
        </div>
      )}
    </div>
  );
}
