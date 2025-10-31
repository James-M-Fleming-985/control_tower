// API Configuration
const isDev = import.meta.env.MODE === 'development';
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (isDev ? 'http://localhost:8000' : '');

export const apiUrl = (path: string): string => {
  return `${API_BASE_URL}${path}`;
};

export default {
  apiUrl,
  isDev,
  isProd: import.meta.env.MODE === 'production',
};