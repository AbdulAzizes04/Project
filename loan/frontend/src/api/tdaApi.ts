import api from './axios';
import { generateMockTDA } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 700) => new Promise(r => setTimeout(r, ms));

export const tdaApi = {
  analyze: async (params?: object) => {
    if (USE_MOCK) { await delay(1200); return generateMockTDA(); }
    const { data } = await api.post('/tda/analyze', params);
    return data;
  },
  getByCompany: async (companyId: string) => {
    if (USE_MOCK) { await delay(600); return generateMockTDA(); }
    const { data } = await api.get(`/tda/${companyId}`);
    return data;
  },
};
