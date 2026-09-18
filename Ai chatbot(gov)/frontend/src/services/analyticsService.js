import api from './api';

export const analyticsService = {
  getDashboardStats: async () => {
    const res = await api.get('/analytics/dashboard');
    return res.data;
  },

  getCategoryBreakdown: async () => {
    const res = await api.get('/analytics/categories');
    return res.data;
  },

  getPriorityBreakdown: async () => {
    const res = await api.get('/analytics/priorities');
    return res.data;
  },

  getStatusDistribution: async () => {
    const res = await api.get('/analytics/status');
    return res.data;
  },

  getDepartmentStats: async () => {
    const res = await api.get('/analytics/departments');
    return res.data;
  },

  getTimeline: async (days = 30) => {
    const res = await api.get(`/analytics/timeline?days=${days}`);
    return res.data;
  },

  getModelMetrics: async () => {
    const res = await api.get('/analytics/models');
    return res.data;
  },

  // Direct AI test inference
  testClassifier: async (text) => {
    const res = await api.post('/ai/classify', { text });
    return res.data;
  },

  testPriority: async (text, category) => {
    const res = await api.post('/ai/priority', { text, category });
    return res.data;
  },

  testDuplicate: async (text, category) => {
    const res = await api.post('/ai/duplicate-check', { text, category });
    return res.data;
  },
};
