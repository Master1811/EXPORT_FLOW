import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
  const [loading, setLoading] = useState(true);
  const refreshTimeoutRef = useRef(null);
  
  // Race condition prevention
  const isRefreshing = useRef(false);
  const failedQueue = useRef([]);

  const processQueue = useCallback((error, token = null) => {
    failedQueue.current.forEach(prom => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });
    failedQueue.current = [];
  }, []);

  const setAuthTokens = useCallback((accessToken, newRefreshToken = null) => {
    if (accessToken) {
      localStorage.setItem('token', accessToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      if (newRefreshToken) {
        localStorage.setItem('refreshToken', newRefreshToken);
        setRefreshToken(newRefreshToken);
      }
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      delete axios.defaults.headers.common['Authorization'];
      setRefreshToken(null);
    }
    setToken(accessToken);
  }, []);

  const performTokenRefresh = useCallback(async (storedRefreshToken) => {
    // Prevent multiple simultaneous refresh calls
    if (isRefreshing.current) {
      return new Promise((resolve, reject) => {
        failedQueue.current.push({ resolve, reject });
      });
    }

    isRefreshing.current = true;

    try {
      const response = await axios.post(`${API}/auth/refresh`, {
        refresh_token: storedRefreshToken
      });
      
      const newToken = response.data.access_token;
      const newRefreshToken = response.data.refresh_token;
      
      setAuthTokens(newToken, newRefreshToken);
      processQueue(null, newToken);
      
      return response.data;
    } catch (error) {
      processQueue(error, null);
      throw error;
    } finally {
      isRefreshing.current = false;
    }
  }, [setAuthTokens, processQueue]);

  const scheduleTokenRefresh = useCallback((expiresIn) => {
    // Clear existing timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    
    // Refresh 1 minute before expiry
    const refreshTime = (expiresIn - 60) * 1000;
    if (refreshTime > 0) {
      refreshTimeoutRef.current = setTimeout(async () => {
        try {
          const storedRefreshToken = localStorage.getItem('refreshToken');
          if (storedRefreshToken) {
            const data = await performTokenRefresh(storedRefreshToken);
            scheduleTokenRefresh(data.expires_in);
          }
        } catch (error) {
          console.error('Scheduled token refresh failed:', error);
          // Don't logout here - let the interceptor handle it
        }
      }, refreshTime);
    }
  }, [performTokenRefresh]);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    setAuthTokens(response.data.access_token, response.data.refresh_token);
    setUser(response.data.user);
    // Schedule token refresh
    if (response.data.expires_in) {
      scheduleTokenRefresh(response.data.expires_in);
    }
    return response.data;
  };

  const register = async (email, password, full_name, company_name) => {
    const response = await axios.post(`${API}/auth/register`, { 
      email, password, full_name, company_name 
    });
    setAuthTokens(response.data.access_token, response.data.refresh_token);
    setUser(response.data.user);
    // Schedule token refresh
    if (response.data.expires_in) {
      scheduleTokenRefresh(response.data.expires_in);
    }
    return response.data;
  };

  const logout = () => {
    // Clear refresh timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    // Clear any pending queue
    failedQueue.current = [];
    isRefreshing.current = false;
    
    setAuthTokens(null);
    setUser(null);
  };

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedRefreshToken = localStorage.getItem('refreshToken');
      
      if (storedToken) {
        try {
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          const response = await axios.get(`${API}/auth/me`);
          setUser(response.data);
          setToken(storedToken);
          setRefreshToken(storedRefreshToken);
          // Schedule refresh for remaining time (assume 15 min default)
          scheduleTokenRefresh(14 * 60); // 14 minutes
        } catch (error) {
          // Try to refresh token
          if (storedRefreshToken) {
            try {
              const refreshResponse = await performTokenRefresh(storedRefreshToken);
              const meResponse = await axios.get(`${API}/auth/me`);
              setUser(meResponse.data);
              scheduleTokenRefresh(refreshResponse.expires_in);
            } catch (refreshError) {
              setAuthTokens(null);
            }
          } else {
            setAuthTokens(null);
          }
        }
      }
      setLoading(false);
    };
    initAuth();
    
    // Cleanup
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [setAuthTokens, scheduleTokenRefresh, performTokenRefresh]);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// API Helper with enhanced interceptor for race condition handling
export const api = axios.create({
  baseURL: API,
});

// Track if we're currently refreshing
let apiIsRefreshing = false;
let apiFailedQueue = [];

const processApiQueue = (error, token = null) => {
  apiFailedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  apiFailedQueue = [];
};

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for auto-refresh with race condition protection
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and we have a refresh token and haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Check if we're already refreshing
      if (apiIsRefreshing) {
        // Queue this request to retry after refresh completes
        return new Promise((resolve, reject) => {
          apiFailedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;
      apiIsRefreshing = true;
      
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const newToken = response.data.access_token;
          localStorage.setItem('token', newToken);
          localStorage.setItem('refreshToken', response.data.refresh_token);
          
          // Process queued requests
          processApiQueue(null, newToken);
          
          // Update header and retry
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect
          processApiQueue(refreshError, null);
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          apiIsRefreshing = false;
        }
      }
    }
    
    return Promise.reject(error);
  }
);
