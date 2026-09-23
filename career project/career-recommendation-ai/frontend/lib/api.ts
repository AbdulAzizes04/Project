// API base — works from browser (proxied via Next.js) or direct
const API_BASE = "/api";

// ---------- Auth Helpers ----------
export const getToken = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem("token") : null;

export const getRole = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem("role") : null;

export const getUserName = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem("name") : null;

export const getUserId = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem("user_id") : null;

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("name");
  localStorage.removeItem("user_id");
  window.location.href = "/login";
};

// ---------- HTTP helpers ----------
async function request<T>(
  path: string,
  options: RequestInit = {},
  auth: boolean = false
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err?.detail?.message || err?.message || res.statusText);
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

// ---------- Auth API ----------
export const api = {
  auth: {
    register: (body: { name: string; email: string; password: string; role?: string }) =>
      request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
    login: async (body: { email: string; password: string }) => {
      const data: any = await request("/auth/login", { method: "POST", body: JSON.stringify(body) });
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("name", data.name || "");
        localStorage.setItem("user_id", String(data.user_id));
      }
      return data;
    },
    me: () => request("/auth/me", {}, true),
  },

  // ---------- Student Profile ----------
  student: {
    getProfile: () => request("/student/profile", {}, true),
    updateProfile: (body: any) =>
      request("/student/profile", { method: "PUT", body: JSON.stringify(body) }, true),
    getAcademic: () => request("/student/academic", {}, true),
    updateAcademic: (body: any) =>
      request("/student/academic", { method: "PUT", body: JSON.stringify(body) }, true),
    getAptitude: () => request("/student/aptitude", {}, true),
    updateAptitude: (body: any) =>
      request("/student/aptitude", { method: "PUT", body: JSON.stringify(body) }, true),
    getInterests: () => request("/student/interests", {}, true),
    updateInterests: (body: any) =>
      request("/student/interests", { method: "PUT", body: JSON.stringify(body) }, true),
  },

  // ---------- Portfolio ----------
  portfolio: {
    getSkills: () => request("/student/skills", {}, true),
    addSkill: (body: { skill_id: number; proficiency_level: string }) =>
      request("/student/skills", { method: "POST", body: JSON.stringify(body) }, true),
    updateSkill: (id: number, body: { proficiency_level: string }) =>
      request(`/student/skills/${id}`, { method: "PUT", body: JSON.stringify(body) }, true),
    deleteSkill: (id: number) =>
      request(`/student/skills/${id}`, { method: "DELETE" }, true),
    getCertifications: () => request("/student/certifications", {}, true),
    addCertification: (body: any) =>
      request("/student/certifications", { method: "POST", body: JSON.stringify(body) }, true),
    deleteCertification: (id: number) =>
      request(`/student/certifications/${id}`, { method: "DELETE" }, true),
    getProjects: () => request("/student/projects", {}, true),
    addProject: (body: any) =>
      request("/student/projects", { method: "POST", body: JSON.stringify(body) }, true),
    deleteProject: (id: number) =>
      request(`/student/projects/${id}`, { method: "DELETE" }, true),
    getSkillsCatalog: () => request("/skills", {}, false),
  },

  // ---------- Recommendations ----------
  recommendations: {
    generate: (regenerate = false) =>
      request("/recommendations/generate", { method: "POST", body: JSON.stringify({ regenerate }) }, true),
    getAll: () => request("/recommendations", {}, true),
    getDetail: (id: number) => request(`/recommendations/${id}`, {}, true),
    getSHAP: (id: number) => request(`/recommendations/${id}/shap`, {}, true),
    getLIME: (id: number) => request(`/recommendations/${id}/lime`, {}, true),
  },

  // ---------- Skill Gap ----------
  skillGap: {
    getForCareer: (careerId: number) => request(`/skill-gap/${careerId}`, {}, true),
    getRoadmap: () => request("/learning-roadmap", {}, true),
  },

  // ---------- Progress ----------
  progress: {
    getAll: () => request("/student/progress", {}, true),
    add: (body: any) =>
      request("/student/progress", { method: "POST", body: JSON.stringify(body) }, true),
    update: (id: number, body: { status: string; progress_percent: number; notes?: string }) =>
      request(`/student/progress/${id}`, { method: "PUT", body: JSON.stringify(body) }, true),
  },

  // ---------- Careers ----------
  careers: {
    getAll: () => request("/careers", {}, false),
    compare: (career_ids: number[]) =>
      request("/careers/compare", { method: "POST", body: JSON.stringify({ career_ids }) }, true),
  },

  // ---------- Admin ----------
  admin: {
    getStudents: () => request("/admin/students", {}, true),
    getCareers: () => request("/admin/careers", {}, true),
    getSkills: () => request("/admin/skills", {}, true),
    getAnalytics: () => request("/admin/analytics", {}, true),
    getModelPerformance: () => request("/admin/model-performance", {}, true),
  },
};
