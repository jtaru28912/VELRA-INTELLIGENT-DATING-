import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  token: string | null;
  acceptedTc: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  acceptTc: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('velra_token'));
  const [acceptedTc, setAcceptedTc] = useState<boolean>(localStorage.getItem('velra_tc_accepted') === 'true');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        try {
          // Token is present, assume valid for now but in a real app we'd call /auth/verify
          // The router.py already handles 401s globally via apiFetch
          localStorage.setItem('velra_token', token);
        } catch (err) {
          logout();
        }
      } else {
        localStorage.removeItem('velra_token');
        localStorage.removeItem('velra_tc_accepted');
      }
      setLoading(false);
    };
    validateToken();
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setToken(data.access_token);
    setAcceptedTc(data.accepted_tc);
    localStorage.setItem('velra_tc_accepted', String(data.accepted_tc));
  };

  const signup = async (email: string, password: string) => {
    const response = await fetch('http://localhost:8000/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    const data = await response.json();
    setToken(data.access_token);
    setAcceptedTc(false);
    localStorage.setItem('velra_tc_accepted', 'false');
  };

  const acceptTc = async () => {
    if (!token) return;
    try {
      const response = await fetch('http://localhost:8000/auth/me/accept-tc', {
        method: 'PATCH',
        headers: { 
          'Authorization': `Bearer ${token}`
        },
      });
      if (response.ok) {
        setAcceptedTc(true);
        localStorage.setItem('velra_tc_accepted', 'true');
      }
    } catch (err) {
      console.error("Failed to accept TC", err);
    }
  };

  const logout = () => {
    setToken(null);
    setAcceptedTc(false);
    localStorage.removeItem('velra_token');
    localStorage.removeItem('velra_tc_accepted');
    // Clear all potential artifacts or state
    sessionStorage.clear();
  };

  if (loading) return null; // Prevent flash of unauthorized content

  return (
    <AuthContext.Provider value={{ 
      token, 
      acceptedTc, 
      login, 
      signup, 
      logout, 
      acceptTc, 
      loading,
      isAuthenticated: !!token 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
