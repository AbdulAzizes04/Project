import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

// ── Cases ──────────────────────────────────────────────────────────────────
export const createCase = (data) => api.post('/api/cases/create', data);
export const listCases = () => api.get('/api/cases');
export const getCase = (id) => api.get(`/api/cases/${id}`);
export const deleteCase = (id) => api.delete(`/api/cases/${id}`);
export const getCaseTracks = (id) => api.get(`/api/cases/${id}/tracks`);
export const getCaseTimeline = (id) => api.get(`/api/cases/${id}/timeline`);
export const getCaseAnalysis = (id) => api.get(`/api/cases/${id}/analysis`);

// ── Analysis ───────────────────────────────────────────────────────────────
export const uploadFiles = (caseId, videoFile, refImage) => {
  const form = new FormData();
  form.append('case_id', caseId);
  if (videoFile) form.append('video', videoFile);
  if (refImage) form.append('reference_image', refImage);
  return api.post('/api/analysis/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const runAnalysis = (data) => api.post('/api/analysis/run', data);
export const getAnalysisStatus = (caseId) => api.get(`/api/analysis/${caseId}/status`);

// ── Chat ───────────────────────────────────────────────────────────────────
export const sendChat = (question, caseId = null) =>
  api.post('/api/chat', { question, case_id: caseId });
export const getChatHistory = (caseId, limit = 20) =>
  api.get('/api/chat/history', { params: { case_id: caseId, limit } });

// ── Reports ────────────────────────────────────────────────────────────────
export const downloadPDF = (caseId) =>
  `${API_BASE}/api/reports/${caseId}/pdf`;
export const downloadDOCX = (caseId) =>
  `${API_BASE}/api/reports/${caseId}/docx`;

// ── Health ─────────────────────────────────────────────────────────────────
export const checkHealth = () => api.get('/api/health');

export default api;
