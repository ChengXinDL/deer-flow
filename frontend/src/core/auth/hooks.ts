"use client";

/**
 * 认证相关的 React Hooks
 */

import { useState, useEffect, useCallback } from "react";
import {
  User,
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from "./types";
import {
  login as loginAPI,
  register as registerAPI,
  logout as logoutAPI,
  getCurrentUser,
  refreshToken,
  forgotPassword as forgotPasswordAPI,
  resetPassword as resetPasswordAPI,
  changePassword as changePasswordAPI,
  isAuthenticated as checkIsAuthenticated,
  getAccessToken,
  getRefreshToken,
} from "./api";

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (request: LoginRequest) => Promise<void>;
  register: (request: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (request: ForgotPasswordRequest) => Promise<void>;
  resetPassword: (request: ResetPasswordRequest) => Promise<void>;
  changePassword: (request: ChangePasswordRequest) => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

/**
 * 认证 Hook
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 初始化时检查登录状态
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (checkIsAuthenticated()) {
          const userData = await getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        }
      } catch (err) {
        // 令牌可能已过期，尝试刷新
        const refreshTokenStr = getRefreshToken();
        if (refreshTokenStr) {
          try {
            await refreshToken(refreshTokenStr);
            const userData = await getCurrentUser();
            setUser(userData);
            setIsAuthenticated(true);
          } catch (refreshErr) {
            // 刷新失败，清除登录状态
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * 登录
   */
  const login = useCallback(async (request: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loginAPI(request);
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "登录失败";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 注册
   */
  const register = useCallback(async (request: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await registerAPI(request);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "注册失败";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 登出
   */
  const logout = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await logoutAPI();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
  }, []);

  /**
   * 忘记密码
   */
  const forgotPassword = useCallback(async (request: ForgotPasswordRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await forgotPasswordAPI(request);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "发送重置链接失败";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 重置密码
   */
  const resetPassword = useCallback(async (request: ResetPasswordRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await resetPasswordAPI(request);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "重置密码失败";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 修改密码
   */
  const changePassword = useCallback(async (request: ChangePasswordRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await changePasswordAPI(request);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "修改密码失败";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 刷新用户信息
   */
  const refreshUser = useCallback(async () => {
    try {
      if (checkIsAuthenticated()) {
        const userData = await getCurrentUser();
        setUser(userData);
      }
    } catch (err) {
      console.error("Failed to refresh user:", err);
    }
  }, []);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    changePassword,
    refreshUser,
    clearError,
  };
}

/**
 * 检查是否已登录
 */
export function useIsAuthenticated(): boolean {
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    setIsAuth(checkIsAuthenticated());
  }, []);

  return isAuth;
}

/**
 * 获取当前用户
 */
export function useCurrentUser(): { user: User | null; isLoading: boolean } {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        if (checkIsAuthenticated()) {
          const userData = await getCurrentUser();
          setUser(userData);
        }
      } catch (err) {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  return { user, isLoading };
}
