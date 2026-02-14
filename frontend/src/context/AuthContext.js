import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // El interceptor en api.js maneja automáticamente el header Authorization
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      // Solo loggear en desarrollo
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Fetch user error:', error.message);
      }
      localStorage.removeItem('token');
      // El interceptor en api.js maneja automáticamente el header Authorization
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login-json', { email, password });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      // El interceptor en api.js maneja automáticamente el header Authorization
      await fetchUser();
      return { success: true };
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Login error:', error.message);
      }
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al iniciar sesión' 
      };
    }
  };

  const register = async (userData) => {
    try {
      await api.post('/auth/register', userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al registrarse' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    // El interceptor en api.js maneja automáticamente el header Authorization
    setUser(null);
  };

  const isProfessional = () => user?.role === 'professional';
  const isAdmin = () => user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      register, 
      loading,
      isProfessional,
      isAdmin
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
