import api from './api';

export const complaintService = {
  createComplaint: async (data) => {
    const res = await api.post('/complaints', data);
    return res.data;
  },

  uploadAttachment: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/complaints/upload', formData);
    return res.data;
  },

  getMyComplaints: async () => {
    const res = await api.get('/complaints/my');
    return res.data;
  },

  getComplaintById: async (id) => {
    const res = await api.get(`/complaints/${id}`);
    return res.data;
  },

  trackByTicketNumber: async (ticketNumber) => {
    const res = await api.get(`/complaints/track/${ticketNumber}`);
    return res.data;
  },

  updateStatus: async (id, status, remarks) => {
    const res = await api.patch(`/complaints/${id}/status`, { status, remarks });
    return res.data;
  },

  assignComplaint: async (id, staffId, departmentId, notes) => {
    const res = await api.post(`/admin/complaints/${id}/assign`, {
      assigned_staff_id: staffId,
      assigned_to_id: staffId,
      department_id: departmentId,
      notes,
    });
    return res.data;
  },

  verifyComplaint: async (id, category, priority, departmentId, notes) => {
    const res = await api.post(`/admin/complaints/${id}/verify`, {
      verified_category: category,
      verified_priority: priority,
      corrected_category: category,
      corrected_priority: priority,
      department_id: departmentId,
      remarks: notes,
      notes,
    });
    return res.data;
  },
};
