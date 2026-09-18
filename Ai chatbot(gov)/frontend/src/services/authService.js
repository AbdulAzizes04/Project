import api from './api';

export const authService = {
  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const token = res.data.access_token || res.data.tokens?.access_token;
    if (token) {
      localStorage.setItem('access_token', token);
    }
    if (res.data.user) {
      localStorage.setItem('user_info', JSON.stringify(res.data.user));
    }
    return res.data;
  },

  register: async (userData) => {
    const res = await api.post('/auth/register', userData);
    const token = res.data.access_token || res.data.tokens?.access_token;
    if (token) {
      localStorage.setItem('access_token', token);
    }
    if (res.data.user) {
      localStorage.setItem('user_info', JSON.stringify(res.data.user));
    }
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  },
};
