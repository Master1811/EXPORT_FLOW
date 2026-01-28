import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
  const [loading, setLoading] = useState(true);

  const setAuthToken = useCallback((newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    } else {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
    setToken(newToken);
  }, []);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    setAuthToken(response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const register = async (email, password, full_name, company_name) => {
    const response = await axios.post(`${API}/auth/register`, { 
      email, password, full_name, company_name 
    });
    setAuthToken(response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const logout = () => {
    setAuthToken(null);
    setUser(null);
  };

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get(`${API}/auth/me`);
          setUser(response.data);
        } catch (error) {
          setAuthToken(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token, setAuthToken]);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// API Helper
export const api = axios.create({
  baseURL: API,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
