"use client";
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getToken } from '../lib/api';

export type UserRole = 'shopkeeper' | 'admin' | 'unknown';

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  email: string | null;
  role: UserRole;
  permissions: string[];
  setToken: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [jwt, setJwt] = useState<string | null>(null);

  useEffect(() => {
    setJwt(getToken());
  }, []);

  const decoded = useMemo(() => {
    if (!jwt) return null;
    try {
      const payload = JSON.parse(atob(jwt.split('.')[1] || ''));
      return payload;
    } catch {
      return null;
    }
  }, [jwt]);

  const role: UserRole = (decoded?.user_metadata?.role || 'shopkeeper') as UserRole;
  const permissions: string[] = decoded?.user_metadata?.permissions || [];

  const value: AuthState = {
    isAuthenticated: !!jwt,
    userId: decoded?.sub || null,
    email: decoded?.email || null,
    role,
    permissions,
    setToken: (token: string) => {
      if (typeof window !== 'undefined') localStorage.setItem('BB_TOKEN', token);
      setJwt(token);
    },
    logout: () => {
      if (typeof window !== 'undefined') localStorage.removeItem('BB_TOKEN');
      setJwt(null);
      if (typeof window !== 'undefined') window.location.href = '/login';
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
