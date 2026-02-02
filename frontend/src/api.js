import axios from 'axios';

/* Backend API base URL */
const API_BASE_URL = 'http://127.0.0.1:8000';

/* Create axios instance with default config */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* Request interceptor - attach JWT token to every request */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/* Response interceptor - handle 401 errors */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      /* Clear tokens and trigger logout */
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      /* Dispatch custom event to notify App component */
      window.dispatchEvent(new Event('auth:logout'));
    }
    return Promise.reject(error);
  }
);

/* Auth helper functions */
export const authService = {
  /* Register a new user account */
  register: async (username, password, confirmPassword, email = '') => {
    const response = await axios.post(`${API_BASE_URL}/api/register/`, {
      username,
      password,
      confirm_password: confirmPassword,
      email: email || undefined,
    });
    return response.data;
  },

  /* Login and store tokens */
  login: async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/api/token/`, {
      username,
      password,
    });
    
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  },

  /* Logout and clear tokens */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  /* Check if user is authenticated */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /* Refresh access token */
  refreshToken: async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      throw new Error('No refresh token');
    }

    const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
      refresh,
    });

    const { access } = response.data;
    localStorage.setItem('access_token', access);
    
    return access;
  },
};

export default api;
