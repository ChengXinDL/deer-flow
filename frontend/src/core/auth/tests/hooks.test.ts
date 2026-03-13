"""认证 Hooks 测试用例"""

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from '../hooks';
import * as authApi from '../api';

// Mock 认证 API
jest.mock('../api');

const mockAuthApi = authApi as jest.Mocked<typeof authApi>;

// 测试数据
const mockUser = {
  id: '123456',
  email: 'test@example.com',
  phone: null,
  name: '测试用户',
  avatar_url: null,
  is_active: true,
  is_verified: false,
  created_at: new Date().toISOString(),
  last_login_at: null
};

const mockTokens = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
};

describe('useAuth Hook 测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // 清除 localStorage
    localStorage.clear();
  });

  it('应该初始化未认证状态', async () => {
    // Mock checkIsAuthenticated 返回 false
    mockAuthApi.checkIsAuthenticated.mockReturnValue(false);

    const { result } = renderHook(() => useAuth());

    // 初始状态
    expect(result.current.isLoading).toBe(true);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.error).toBe(null);

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });

  it('应该在有令牌时初始化认证状态', async () => {
    // Mock checkIsAuthenticated 返回 true
    mockAuthApi.checkIsAuthenticated.mockReturnValue(true);
    // Mock getCurrentUser 返回用户信息
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(mockAuthApi.getCurrentUser).toHaveBeenCalled();
  });

  it('应该处理登录成功', async () => {
    // Mock login 返回令牌
    mockAuthApi.login.mockResolvedValue({
      ...mockTokens,
      user_name: mockUser.name,
      user_avatar: mockUser.avatar_url
    });
    // Mock getCurrentUser 返回用户信息
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 执行登录
    await act(async () => {
      await result.current.login({
        login_type: 'email',
        identifier: 'test@example.com',
        password: 'Test123456',
        remember_me: true
      });
    });

    // 验证登录结果
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(mockAuthApi.login).toHaveBeenCalledWith({
      login_type: 'email',
      identifier: 'test@example.com',
      password: 'Test123456',
      remember_me: true
    });
    expect(mockAuthApi.getCurrentUser).toHaveBeenCalled();
  });

  it('应该处理登录失败', async () => {
    // Mock login 抛出错误
    mockAuthApi.login.mockRejectedValue(new Error('账号或密码错误'));

    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 执行登录
    await act(async () => {
      try {
        await result.current.login({
          login_type: 'email',
          identifier: 'test@example.com',
          password: 'wrong password',
          remember_me: false
        });
      } catch (error) {
        // 错误已在 hook 中处理
      }
    });

    // 验证登录失败结果
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.error).toBe('账号或密码错误');
  });

  it('应该处理注册成功', async () => {
    // Mock register 返回用户信息
    mockAuthApi.register.mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 执行注册
    await act(async () => {
      await result.current.register({
        email: 'test@example.com',
        password: 'Test123456',
        name: '测试用户'
      });
    });

    // 验证注册结果
    expect(mockAuthApi.register).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'Test123456',
      name: '测试用户'
    });
  });

  it('应该处理登出', async () => {
    // 先设置认证状态
    mockAuthApi.checkIsAuthenticated.mockReturnValue(true);
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);
    mockAuthApi.logout.mockResolvedValue({ message: '登出成功' });

    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    // 执行登出
    await act(async () => {
      await result.current.logout();
    });

    // 验证登出结果
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(mockAuthApi.logout).toHaveBeenCalled();
  });

  it('应该清除错误', async () => {
    const { result } = renderHook(() => useAuth());

    // 等待初始化完成
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 模拟错误状态
    await act(async () => {
      try {
        await result.current.login({
          login_type: 'email',
          identifier: 'test@example.com',
          password: 'wrong password',
          remember_me: false
        });
      } catch (error) {
        // 错误已在 hook 中处理
      }
    });

    // 验证错误存在
    expect(result.current.error).toBeTruthy();

    // 清除错误
    act(() => {
      result.current.clearError();
    });

    // 验证错误已清除
    expect(result.current.error).toBe(null);
  });
});
