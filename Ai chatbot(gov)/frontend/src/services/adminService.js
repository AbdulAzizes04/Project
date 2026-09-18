import api from './api';

export const adminService = {
  getDashboardStats: async () => {
    const res = await api.get('/admin/dashboard');
    return res.data;
  },

  listUsers: async (params = {}) => {
    const res = await api.get('/admin/users', { params });
    return res.data;
  },

  createStaff: async (staffData) => {
    const res = await api.post('/admin/staff', staffData);
    return res.data;
  },

  listStaff: async (departmentId) => {
    const params = departmentId ? { department_id: departmentId } : {};
    const res = await api.get('/admin/staff', { params });
    return res.data;
  },

  updateUser: async (userId, updates) => {
    const res = await api.put(`/admin/users/${userId}`, updates);
    return res.data;
  },

  listDepartments: async () => {
    const res = await api.get('/departments');
    return res.data;
  },

  createDepartment: async (deptData) => {
    const res = await api.post('/departments', deptData);
    return res.data;
  },

  updateDepartment: async (id, deptData) => {
    const res = await api.put(`/departments/${id}`, deptData);
    return res.data;
  },

  listAllComplaints: async (params = {}) => {
    const res = await api.get('/complaints', { params });
    return res.data;
  },
};
