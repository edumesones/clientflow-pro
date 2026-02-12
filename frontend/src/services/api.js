import axios from 'axios';

// Force rebuild: 2026-02-12 - API URL fix
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
console.log('API URL:', API_URL); // Debug

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
