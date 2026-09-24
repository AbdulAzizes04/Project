import api from './axios';
import type { PredictionInput, PredictionResult } from '@/types';
import { generatePredictionResult, mockPredictionHistory } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const delay = (ms = 1800) => new Promise(r => setTimeout(r, ms));

export const predictionApi = {
  predict: async (input: PredictionInput): Promise<PredictionResult> => {
    if (USE_MOCK) {
      await delay(2000);
      return generatePredictionResult(input);
    }
    const { data } = await api.post('/predictions', input);
    return data;
  },

  getById: async (id: string) => {
    if (USE_MOCK) {
      await delay(500);
      return mockPredictionHistory.find(p => p.id === id);
    }
    const { data } = await api.get(`/predictions/${id}`);
    return data;
  },

  getHistory: async (params?: { page?: number; pageSize?: number; risk?: string; model?: string }) => {
    if (USE_MOCK) {
      await delay(600);
      const page = params?.page || 1;
      const pageSize = params?.pageSize || 10;
      let filtered = [...mockPredictionHistory];
      if (params?.risk) filtered = filtered.filter(p => p.riskCategory === params.risk);
      if (params?.model) filtered = filtered.filter(p => p.modelUsed === params.model);
      const total = filtered.length;
      const data = filtered.slice((page - 1) * pageSize, page * pageSize);
      return { data, total, page, pageSize, totalPages: Math.ceil(total / pageSize) };
    }
    const { data } = await api.get('/predictions', { params });
    return data;
  },
};
