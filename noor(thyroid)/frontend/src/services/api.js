import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Attach token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401
API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ───────────────────────────────────────────────────────────────────────
export const authAPI = {
  login:   (data) => API.post('/auth/login', data),
  me:      ()     => API.get('/auth/me'),
  register:(data) => API.post('/auth/register', data),
}

// ── Patients ──────────────────────────────────────────────────────────────────
export const patientsAPI = {
  create:  (data)     => API.post('/patients/', data),
  list:    (params)   => API.get('/patients/', { params }),
  get:     (id)       => API.get(`/patients/${id}`),
  update:  (id, data) => API.put(`/patients/${id}`, data),
  delete:  (id)       => API.delete(`/patients/${id}`),
  count:   ()         => API.get('/patients/count'),
}

// ── Predictions ───────────────────────────────────────────────────────────────
export const predictionsAPI = {
  predict:  (data)   => API.post('/predictions/', data),
  list:     (params) => API.get('/predictions/', { params }),
  get:      (id)     => API.get(`/predictions/${id}`),
  stats:    ()       => API.get('/predictions/stats'),
  delete:   (id)     => API.delete(`/predictions/${id}`),
}

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsAPI = {
  generate: (predId) => API.post(`/reports/generate/${predId}`),
  list:     ()       => API.get('/reports/list'),
  download: (filename) => `/reports/${filename}`,
}

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminAPI = {
  analytics:       ()       => API.get('/admin/analytics'),
  modelPerformance:()       => API.get('/admin/model-performance'),
  notifications:   ()       => API.get('/admin/notifications'),
  markRead:        (id)     => API.patch(`/admin/notifications/${id}/read`),
  markAllRead:     ()       => API.patch('/admin/notifications/read-all'),
  users:           ()       => API.get('/admin/users'),
  createUser:      (data)   => API.post('/admin/users', data),
  deleteUser:      (id)     => API.delete(`/admin/users/${id}`),
  uploadDataset:   (form)   => API.post('/admin/upload-dataset', form, { headers: {'Content-Type':'multipart/form-data'} }),
  exportCSV:       ()       => '/api/admin/export/predictions',
}

// ── OCR ───────────────────────────────────────────────────────────────────────
export const ocrAPI = {
  extract: (form) => API.post('/ocr/extract', form, { headers: {'Content-Type':'multipart/form-data'} }),
}

// ── Appointments ──────────────────────────────────────────────────────────────
export const appointmentsAPI = {
  create:       (data)         => API.post('/appointments/', data),
  list:         ()             => API.get('/appointments/'),
  updateStatus: (id, status)   => API.patch(`/appointments/${id}/status?status=${status}`),
  delete:       (id)           => API.delete(`/appointments/${id}`),
}

export default API
