import axios from 'axios';

/* ==============================
   Backend API base URL
   ============================== */

/*
  IMPORTANT:
  - Local: use .env with REACT_APP_API_BASE_URL=http://127.0.0.1:8000
  - Production (Vercel): set env variable in Vercel dashboard
*/
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

/* ==============================
   Axios instance
   ============================== */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* ==============================
   Request interceptor
   Attach JWT token
   ============================== */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ==============================
   Response interceptor
   Handle 401 (token expired)
   ============================== */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      /* Notify app to logout */
      window.dispatchEvent(new Event('auth:logout'));
    }
    return Promise.reject(error);
  }
);

/* ==============================
   Authentication Service
   ============================== */
export const authService = {
  /* Register new user */
  register: async (username, password, confirmPassword, email = '') => {
    const response = await axios.post(`${API_BASE_URL}/api/register/`, {
      username,
      password,
      confirm_password: confirmPassword,
      email: email || undefined,
    });
    return response.data;
  },

  /* Login user */
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

  /* Logout */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  /* Auth check */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /* Refresh token */
  refreshToken: async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      throw new Error('No refresh token');
    }

    const response = await axios.post(
      `${API_BASE_URL}/api/token/refresh/`,
      { refresh }
    );

    const { access } = response.data;
    localStorage.setItem('access_token', access);

    return access;
  },
};

export default api;
