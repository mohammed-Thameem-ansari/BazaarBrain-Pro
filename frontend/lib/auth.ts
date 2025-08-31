import API from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    email: string;
  };
  error?: string;
}

export const authAPI = {
  // Login with email and password
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await API.post('/auth/login', credentials);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  },

  // Register new user
  register: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await API.post('/auth/register', credentials);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      const response = await API.get('/auth/me');
      return response.data;
    } catch (error: any) {
      return null;
    }
  },

  // Logout (clear token on client side)
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('BB_TOKEN');
      window.location.href = '/login';
    }
  },
};
