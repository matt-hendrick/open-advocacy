import axios from 'axios';

// Get the base URL from environment variable or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null,
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('Starting API request:', request.url);
  return request;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    console.error('API request failed:', error);
    return Promise.reject(error);
  }
);

export default api;
