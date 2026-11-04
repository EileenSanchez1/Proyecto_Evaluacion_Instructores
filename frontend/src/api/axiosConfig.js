import axios from 'axios';

// Usa VITE_API_URL en .env del frontend para apuntar a un backend de red
// (ej. http://192.168.1.10:8000). Así fotos y API funcionan en todos los PCs.
const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type'];
        delete config.headers['content-type'];
      }
    }
    // Si se forzó Content-Type: undefined, quitarlo
    if (config.headers && config.headers['Content-Type'] === undefined) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      let eraInstructor = false;
      try {
        const u = JSON.parse(localStorage.getItem('usuario') || 'null');
        eraInstructor = u?.rol === 'Instructor';
      } catch {
        /* ignore */
      }
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      window.location.href = eraInstructor ? '/login-instructor' : '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
