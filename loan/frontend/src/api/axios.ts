import axios from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

instance.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

instance.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status;
    const messages: Record<number, string> = {
      401: 'Your session has expired. Please sign in again.',
      400: 'Please check the submitted information.',
      403: 'You do not have permission to perform this action.',
      404: 'The requested resource was not found.',
      500: 'Unable to process the request. Please try again.',
    };
    const message = messages[status] || error.message || 'Unable to connect to the risk analysis server.';
    return Promise.reject({ ...error, userMessage: message });
  }
);

export default instance;
