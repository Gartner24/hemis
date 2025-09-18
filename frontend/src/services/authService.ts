import { config } from '../config/environment';

const API_BASE_URL = config.API_BASE_URL;

interface LoginResponse {
  user: {
    user_id: number;
    email: string;
    full_name: string;
    roles: string[];
    role: string;
  };
  message: string;
}

interface UserResponse {
  user_id: number;
  email: string;
  full_name: string;
  roles: string[];
  role: string;
}

class AuthService {
  private backendAvailable: boolean = true;

  private async checkBackendHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        credentials: 'include',
      });
      this.backendAvailable = response.ok;
      return response.ok;
    } catch (error) {
      this.backendAvailable = false;
      return false;
    }
  }

  async login(email: string, password: string): Promise<UserResponse> {
    // Check backend health before attempting login
    if (!this.backendAvailable) {
      const isHealthy = await this.checkBackendHealth();
      if (!isHealthy) {
        throw new Error('Backend server is not available');
      }
    }

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    return data.user;
  }

  async logout(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Logout failed');
    }
  }

  async getCurrentUser(): Promise<UserResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 401) {
          // User not authenticated
          return null;
        }
        if (response.status === 500) {
          // Server error - might be corrupted session
          console.warn('Server error on auth check - clearing session cookies');
          // Clear any potentially corrupted cookies
          document.cookie.split(';').forEach(function (c) {
            document.cookie = c
              .replace(/^ +/, '')
              .replace(
                /=.*/,
                '=;expires=' + new Date().toUTCString() + ';path=/'
              );
          });
          return null;
        }
        // Other HTTP errors
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.user;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Failed to fetch')) {
        // Connection refused or network error
        throw new Error('Failed to fetch - Backend not available');
      }
      console.error('Error getting current user:', error);
      throw error;
    }
  }

  async validateSession(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        credentials: 'include',
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  async getUserRoles(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/roles`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to get user roles');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user roles:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();
