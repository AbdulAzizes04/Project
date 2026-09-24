import api from './axios';
import { mockNetworkGraph } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 700) => new Promise(r => setTimeout(r, ms));

export const networkApi = {
  getGraph: async () => {
    if (USE_MOCK) { await delay(); return mockNetworkGraph; }
    const { data } = await api.get('/network');
    return data;
  },
  getByCompany: async (companyId: string) => {
    if (USE_MOCK) { await delay(500); return mockNetworkGraph; }
    const { data } = await api.get(`/network/${companyId}`);
    return data;
  },
};
