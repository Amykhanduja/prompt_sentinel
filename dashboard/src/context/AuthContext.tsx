import React, { createContext, useContext, useState, useEffect } from 'react';
import { getAuthToken, removeAuthToken, apiClient } from '../services/apiClient';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = () => {
    removeAuthToken();
    setUser(null);
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const res = await apiClient('/api/v1/auth/me');
          if (res.ok) {
            const userData = await res.json();
            setUser(userData);
          } else {
            logout();
          }
        } catch (err) {
          logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = (_token: string, userData: User) => {
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
