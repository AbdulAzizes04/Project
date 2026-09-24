import api from './axios';
import { mockDashboardSummary, mockTrendData, mockRiskDistribution, mockRiskFactors } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 500) => new Promise(r => setTimeout(r, ms));

export const dashboardApi = {
  getSummary: async () => {
    if (USE_MOCK) { await delay(); return mockDashboardSummary; }
    const { data } = await api.get('/dashboard/summary');
    return data;
  },
  getTrend: async (period: string = '30d') => {
    if (USE_MOCK) { await delay(400); return mockTrendData[period] || mockTrendData['30d']; }
    const { data } = await api.get('/dashboard/trend', { params: { period } });
    return data;
  },
  getRiskDistribution: async () => {
    if (USE_MOCK) { await delay(300); return mockRiskDistribution; }
    const { data } = await api.get('/dashboard/risk-distribution');
    return data;
  },
  getRiskFactors: async () => {
    if (USE_MOCK) { await delay(300); return mockRiskFactors; }
    const { data } = await api.get('/dashboard/risk-factors');
    return data;
  },
};
