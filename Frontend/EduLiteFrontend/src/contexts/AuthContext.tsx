// src/contexts/AuthContext.tsx
import React, { createContext, useState, useEffect, ReactNode } from "react";
import toast from "react-hot-toast";
import {
  initializeTokenService,
  setLogoutHandler,
  setStoredTokens,
  clearStoredTokens,
  shouldBeAuthenticated,
} from "../services/tokenService";

// Type definition for the Auth context value
export interface AuthContextType {
  isLoggedIn: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  loading: boolean;
}

// Type definition for AuthProvider props
interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Logout function that clears tokens and updates state
  const logout = (): void => {
    clearStoredTokens();
    setIsLoggedIn(false);
    toast.success("Logged out successfully 👋");
  };

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuthStatus = (): void => {
      // Use token service to check if user should be authenticated
      const shouldAuth = shouldBeAuthenticated();
      setIsLoggedIn(shouldAuth);
      setLoading(false);
    };

    // Initialize token service with axios interceptors
    initializeTokenService();

    // Set logout handler for token service to use
    setLogoutHandler(logout);

    checkAuthStatus();
  }, []);

  const login = (accessToken: string, refreshToken: string): void => {
    // Use token service to store tokens
    setStoredTokens(accessToken, refreshToken);
    setIsLoggedIn(true);
  };

  const value: AuthContextType = {
    isLoggedIn,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
