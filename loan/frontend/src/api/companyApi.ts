import api from './axios';
import { mockCompanies, getMockCompanyDetail } from '@/services/mock/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const delay = (ms = 600) => new Promise(r => setTimeout(r, ms));

export const companyApi = {
  getAll: async (params?: { page?: number; pageSize?: number; risk?: string; search?: string }) => {
    if (USE_MOCK) {
      await delay();
      let filtered = [...mockCompanies];
      if (params?.risk) filtered = filtered.filter(c => c.riskCategory === params.risk);
      if (params?.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(c => c.name.toLowerCase().includes(q) || c.country.toLowerCase().includes(q));
      }
      const page = params?.page || 1;
      const pageSize = params?.pageSize || 10;
      const total = filtered.length;
      return { data: filtered.slice((page - 1) * pageSize, page * pageSize), total, page, pageSize, totalPages: Math.ceil(total / pageSize) };
    }
    const { data } = await api.get('/companies', { params });
    return data;
  },

  getById: async (id: string) => {
    if (USE_MOCK) {
      await delay(800);
      return getMockCompanyDetail(id);
    }
    const { data } = await api.get(`/companies/${id}`);
    return data;
  },

  getHighRisk: async (limit = 8) => {
    if (USE_MOCK) {
      await delay(400);
      return mockCompanies.filter(c => c.riskCategory === 'HIGH').slice(0, limit);
    }
    const { data } = await api.get('/companies/high-risk', { params: { limit } });
    return data;
  },
};
