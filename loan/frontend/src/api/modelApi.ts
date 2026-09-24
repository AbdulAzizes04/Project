import api from './axios';
import { mockModelMetrics, generateROCCurve, generatePRCurve, mockConfusionMatrix, mockFeatureImportance } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 600) => new Promise(r => setTimeout(r, ms));

export const modelApi = {
  getAll: async () => {
    if (USE_MOCK) { await delay(); return mockModelMetrics; }
    const { data } = await api.get('/models');
    return data;
  },
  getPerformance: async (model: string) => {
    if (USE_MOCK) {
      await delay(800);
      return {
        metrics: mockModelMetrics.find(m => m.model === model),
        roc: generateROCCurve(),
        pr: generatePRCurve(),
        confusion: mockConfusionMatrix,
        featureImportance: mockFeatureImportance,
      };
    }
    const { data } = await api.get('/models/performance', { params: { model } });
    return data;
  },
};
