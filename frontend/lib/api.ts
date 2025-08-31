import axios from 'axios';

// Create axios instance with base configuration
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to inject JWT token
API.interceptors.request.use(
  (config) => {
    // Only run on client side
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('BB_TOKEN');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
API.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Clear invalid token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('BB_TOKEN');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Helper function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('BB_TOKEN');
};

// Helper function to get current token
export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('BB_TOKEN');
};

// Helper function to logout user
export const logout = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('BB_TOKEN');
    window.location.href = '/login';
  }
};

export default API;
