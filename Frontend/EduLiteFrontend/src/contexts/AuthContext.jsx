// src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  initializeTokenService,
  setLogoutHandler,
  setStoredTokens,
  clearStoredTokens,
  shouldBeAuthenticated,
} from "../services/tokenService";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  // Logout function that clears tokens and updates state
  const logout = () => {
    clearStoredTokens();
    setIsLoggedIn(false);
    toast.success("Logged out successfully 👋");
  };

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuthStatus = () => {
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

  const login = (accessToken, refreshToken) => {
    // Use token service to store tokens
    setStoredTokens(accessToken, refreshToken);
    setIsLoggedIn(true);
  };

  const value = {
    isLoggedIn,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
