// src/hooks/useAuth.ts
import { useContext } from "react";
import AuthContext, { AuthContextType } from "../contexts/AuthContext";

/**
 * Custom hook to access the Auth context
 * @throws Error if used outside of AuthProvider
 * @returns AuthContextType with login, logout, isLoggedIn, and loading
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
