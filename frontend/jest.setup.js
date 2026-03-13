// Jest 测试设置文件

// Mock localStorage
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock fetch API
global.fetch = jest.fn();

// Mock console.error 以避免测试中的错误输出干扰
console.error = jest.fn();
