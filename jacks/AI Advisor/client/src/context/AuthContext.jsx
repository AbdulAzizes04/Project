import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Set default auth headers for axios
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
      fetchUserProfile();
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
      setUser(null);
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const res = await axios.get(`${API_URL}/auth/profile`);
      setUser(res.data);
    } catch (err) {
      console.error('Failed to load user profile, token might be expired:', err.message);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      setToken(res.data.token);
      setUser(res.data.user);
      return { success: true };
    } catch (err) {
      console.error('Login error:', err.response?.data?.message || err.message);
      return {
        success: false,
        message: err.response?.data?.message || 'Login failed'
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/auth/register`, { username, email, password });
      setToken(res.data.token);
      setUser(res.data.user);
      return { success: true };
    } catch (err) {
      console.error('Registration error:', err.response?.data?.message || err.message);
      return {
        success: false,
        message: err.response?.data?.message || 'Registration failed'
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
