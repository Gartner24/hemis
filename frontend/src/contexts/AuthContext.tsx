import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService';

interface User {
  user_id: number;
  email: string;
  full_name: string;
  roles: string[];
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
          console.log('User automatically logged in:', currentUser.email);
        }
      } catch (error) {
        // Check if it's a connection error vs authentication error
        if (
          error instanceof Error &&
          error.message.includes('Failed to fetch')
        ) {
          console.log('Backend not available, will retry...');
          // Retry after a short delay
          setTimeout(() => {
            checkAuth();
          }, 2000);
          return; // Don't set loading to false yet
        }
        console.log('No authenticated user found');
      } finally {
        setLoading(false);
      }
    };

    // Only check auth if we're not on the login page
    // This prevents unnecessary auth checks that cause 500 errors
    if (window.location.pathname !== '/login') {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const userData = await authService.login(email, password);
      setUser(userData);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
