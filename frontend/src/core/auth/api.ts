"use client";

/**
 * 认证相关的 API 服务
 */

import { getBackendBaseURL } from "@/core/config";
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  MessageResponse,
  User,
} from "./types";

const API_BASE_URL = getBackendBaseURL();

/**
 * 获取认证相关的 API 基础 URL
 */
function getAuthBaseURL(): string {
  if (API_BASE_URL) {
    return `${API_BASE_URL}/api/auth`;
  }
  // 如果没有配置后端 URL，使用相对路径
  return "/api/auth";
}

/**
 * 发送 HTTP 请求
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getAuthBaseURL()}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  // 添加认证令牌
  const accessToken = localStorage.getItem("access_token");
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * 用户登录
 */
export async function login(request: LoginRequest): Promise<LoginResponse> {
  const response = await fetchAPI<LoginResponse>("/login", {
    method: "POST",
    body: JSON.stringify(request),
  });
  
  // 保存令牌到 localStorage
  localStorage.setItem("access_token", response.access_token);
  localStorage.setItem("refresh_token", response.refresh_token);
  
  return response;
}

/**
 * 用户注册
 */
export async function register(request: RegisterRequest): Promise<RegisterResponse> {
  return fetchAPI<RegisterResponse>("/register", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * 刷新令牌
 */
export async function refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
  const response = await fetchAPI<RefreshTokenResponse>("/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  
  // 更新令牌
  localStorage.setItem("access_token", response.access_token);
  localStorage.setItem("refresh_token", response.refresh_token);
  
  return response;
}

/**
 * 用户登出
 */
export async function logout(): Promise<MessageResponse> {
  const refreshToken = localStorage.getItem("refresh_token");
  
  try {
    if (refreshToken) {
      await fetchAPI<MessageResponse>("/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
  } finally {
    // 清除本地存储的令牌
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
  
  return { message: "登出成功" };
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<User> {
  return fetchAPI<User>("/me");
}

/**
 * 忘记密码
 */
export async function forgotPassword(request: ForgotPasswordRequest): Promise<MessageResponse> {
  return fetchAPI<MessageResponse>("/forgot-password", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * 重置密码
 */
export async function resetPassword(request: ResetPasswordRequest): Promise<MessageResponse> {
  return fetchAPI<MessageResponse>("/reset-password", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * 修改密码
 */
export async function changePassword(request: ChangePasswordRequest): Promise<MessageResponse> {
  return fetchAPI<MessageResponse>("/change-password", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * 更新用户信息
 */
export async function updateUser(data: { name?: string; avatar_url?: string }): Promise<User> {
  return fetchAPI<User>("/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return !!localStorage.getItem("access_token");
}

/**
 * 获取访问令牌
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem("access_token");
}

/**
 * 获取刷新令牌
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem("refresh_token");
}
