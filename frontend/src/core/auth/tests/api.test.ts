"""认证 API 测试用例"""

import * as authApi from '../api';

// Mock fetch API
global.fetch = jest.fn();

const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

// 测试数据
const testUser = {
  name: '测试用户',
  email: 'test@example.com',
  password: 'Test123456'
};

const mockTokens = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
};

const mockUser = {
  id: '123456',
  email: testUser.email,
  phone: null,
  name: testUser.name,
  avatar_url: null,
  is_active: true,
  is_verified: false,
  created_at: new Date().toISOString(),
  last_login_at: null
};

describe('认证 API 测试', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // 清除 localStorage
    localStorage.clear();
  });

  describe('register', () => {
    it('应该成功注册用户', async () => {
      // Mock 响应
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockUser
      } as Response);

      // 调用注册 API
      const result = await authApi.register({
        email: testUser.email,
        password: testUser.password,
        name: testUser.name
      });

      // 验证结果
      expect(result).toEqual(mockUser);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/auth/register',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: testUser.email,
            password: testUser.password,
            name: testUser.name
          })
        }
      );
    });

    it('应该处理注册失败', async () => {
      // Mock 错误响应
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ detail: '邮箱已存在' })
      } as Response);

      // 验证错误处理
      await expect(authApi.register({
        email: testUser.email,
        password: testUser.password,
        name: testUser.name
      })).rejects.toThrow('邮箱已存在');
    });
  });

  describe('login', () => {
    it('应该成功登录并保存令牌', async () => {
      // Mock 响应
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          ...mockTokens,
          user_name: testUser.name,
          user_avatar: null
        })
      } as Response);

      // 调用登录 API
      const result = await authApi.login({
        login_type: 'email',
        identifier: testUser.email,
        password: testUser.password,
        remember_me: true
      });

      // 验证结果
      expect(result).toEqual({
        ...mockTokens,
        user_name: testUser.name,
        user_avatar: null
      });
      
      // 验证令牌是否保存到 localStorage
      expect(localStorage.getItem('access_token')).toBe(mockTokens.access_token);
      expect(localStorage.getItem('refresh_token')).toBe(mockTokens.refresh_token);
    });

    it('应该处理登录失败', async () => {
      // Mock 错误响应
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: '账号或密码错误' })
      } as Response);

      // 验证错误处理
      await expect(authApi.login({
        login_type: 'email',
        identifier: testUser.email,
        password: 'wrong password',
        remember_me: false
      })).rejects.toThrow('账号或密码错误');
    });
  });

  describe('logout', () => {
    it('应该成功登出并清除令牌', async () => {
      // 先设置令牌
      localStorage.setItem('access_token', mockTokens.access_token);
      localStorage.setItem('refresh_token', mockTokens.refresh_token);

      // Mock 响应
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ message: '登出成功' })
      } as Response);

      // 调用登出 API
      const result = await authApi.logout();

      // 验证结果
      expect(result).toEqual({ message: '登出成功' });
      
      // 验证令牌是否从 localStorage 清除
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('应该成功获取当前用户信息', async () => {
      // 先设置令牌
      localStorage.setItem('access_token', mockTokens.access_token);

      // Mock 响应
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockUser
      } as Response);

      // 调用获取用户信息 API
      const result = await authApi.getCurrentUser();

      // 验证结果
      expect(result).toEqual(mockUser);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/auth/me',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${mockTokens.access_token}`
          }
        }
      );
    });

    it('应该处理未授权错误', async () => {
      // 先设置无效令牌
      localStorage.setItem('access_token', 'invalid-token');

      // Mock 错误响应
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Could not validate credentials' })
      } as Response);

      // 验证错误处理
      await expect(authApi.getCurrentUser()).rejects.toThrow('Could not validate credentials');
    });
  });

  describe('refreshToken', () => {
    it('应该成功刷新令牌', async () => {
      // 先设置刷新令牌
      localStorage.setItem('refresh_token', mockTokens.refresh_token);

      // Mock 响应
      const newTokens = {
        ...mockTokens,
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => newTokens
      } as Response);

      // 调用刷新令牌 API
      const result = await authApi.refreshToken();

      // 验证结果
      expect(result).toEqual(newTokens);
      
      // 验证新令牌是否保存到 localStorage
      expect(localStorage.getItem('access_token')).toBe(newTokens.access_token);
      expect(localStorage.getItem('refresh_token')).toBe(newTokens.refresh_token);
    });
  });

  describe('checkIsAuthenticated', () => {
    it('应该在有令牌时返回 true', () => {
      // 设置令牌
      localStorage.setItem('access_token', mockTokens.access_token);
      
      const result = authApi.checkIsAuthenticated();
      expect(result).toBe(true);
    });

    it('应该在没有令牌时返回 false', () => {
      // 清除令牌
      localStorage.removeItem('access_token');
      
      const result = authApi.checkIsAuthenticated();
      expect(result).toBe(false);
    });
  });
});
