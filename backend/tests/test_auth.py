"""认证系统测试用例"""

import pytest
import requests
import json
from datetime import datetime

# 测试基础 URL
BASE_URL = "http://localhost:8001"
AUTH_URL = f"{BASE_URL}/api/auth"

# 测试数据
TEST_USER = {
    "name": "测试用户",
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "password": "Test123456"
}


def test_register():
    """测试用户注册功能"""
    print("=== 测试注册功能 ===")
    print(f"注册用户: {TEST_USER['email']}")
    
    response = requests.post(
        f"{AUTH_URL}/register",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"注册响应状态码: {response.status_code}")
    print(f"注册响应内容: {response.text}")
    
    assert response.status_code == 200, f"注册失败: {response.text}"
    data = response.json()
    assert "id" in data, "响应中缺少用户 ID"
    assert "email" in data, "响应中缺少邮箱"
    assert data["email"] == TEST_USER["email"], "邮箱不匹配"
    assert "name" in data, "响应中缺少姓名"
    assert data["name"] == TEST_USER["name"], "姓名不匹配"
    
    print("✅ 注册测试通过！")
    return data


def test_login():
    """测试用户登录功能"""
    print("\n=== 测试登录功能 ===")
    
    login_data = {
        "login_type": "email",
        "identifier": TEST_USER["email"],
        "password": TEST_USER["password"],
        "remember_me": True
    }
    
    response = requests.post(
        f"{AUTH_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    assert response.status_code == 200, f"登录失败: {response.text}"
    data = response.json()
    assert "access_token" in data, "响应中缺少访问令牌"
    assert "refresh_token" in data, "响应中缺少刷新令牌"
    assert "token_type" in data, "响应中缺少令牌类型"
    assert data["token_type"] == "bearer", "令牌类型不正确"
    assert "expires_in" in data, "响应中缺少过期时间"
    
    print("✅ 登录测试通过！")
    return data


def test_get_current_user():
    """测试获取当前用户信息"""
    print("\n=== 测试获取当前用户信息 ===")
    
    # 先登录获取令牌
    login_data = {
        "login_type": "email",
        "identifier": TEST_USER["email"],
        "password": TEST_USER["password"],
        "remember_me": True
    }
    
    login_response = requests.post(
        f"{AUTH_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert login_response.status_code == 200, f"登录失败: {login_response.text}"
    login_data = login_response.json()
    access_token = login_data["access_token"]
    
    # 使用令牌获取用户信息
    response = requests.get(
        f"{AUTH_URL}/me",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    print(f"获取用户信息响应状态码: {response.status_code}")
    print(f"获取用户信息响应内容: {response.text}")
    
    assert response.status_code == 200, f"获取用户信息失败: {response.text}"
    user_data = response.json()
    assert "id" in user_data, "响应中缺少用户 ID"
    assert "email" in user_data, "响应中缺少邮箱"
    assert user_data["email"] == TEST_USER["email"], "邮箱不匹配"
    assert "name" in user_data, "响应中缺少姓名"
    assert user_data["name"] == TEST_USER["name"], "姓名不匹配"
    
    print("✅ 获取用户信息测试通过！")
    return user_data


def test_refresh_token():
    """测试刷新令牌功能"""
    print("\n=== 测试刷新令牌功能 ===")
    
    # 先登录获取令牌
    login_data = {
        "login_type": "email",
        "identifier": TEST_USER["email"],
        "password": TEST_USER["password"],
        "remember_me": True
    }
    
    login_response = requests.post(
        f"{AUTH_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert login_response.status_code == 200, f"登录失败: {login_response.text}"
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]
    
    # 刷新令牌
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        f"{AUTH_URL}/refresh",
        json=refresh_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"刷新令牌响应状态码: {response.status_code}")
    print(f"刷新令牌响应内容: {response.text}")
    
    assert response.status_code == 200, f"刷新令牌失败: {response.text}"
    data = response.json()
    assert "access_token" in data, "响应中缺少访问令牌"
    assert "refresh_token" in data, "响应中缺少刷新令牌"
    assert "token_type" in data, "响应中缺少令牌类型"
    assert data["token_type"] == "bearer", "令牌类型不正确"
    
    print("✅ 刷新令牌测试通过！")
    return data


def test_logout():
    """测试登出功能"""
    print("\n=== 测试登出功能 ===")
    
    # 先登录获取令牌
    login_data = {
        "login_type": "email",
        "identifier": TEST_USER["email"],
        "password": TEST_USER["password"],
        "remember_me": True
    }
    
    login_response = requests.post(
        f"{AUTH_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert login_response.status_code == 200, f"登录失败: {login_response.text}"
    login_data = login_response.json()
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    
    # 登出
    logout_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        f"{AUTH_URL}/logout",
        json=logout_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    print(f"登出响应状态码: {response.status_code}")
    print(f"登出响应内容: {response.text}")
    
    assert response.status_code == 200, f"登出失败: {response.text}"
    data = response.json()
    assert "message" in data, "响应中缺少消息"
    assert data["message"] == "登出成功", "登出消息不正确"
    
    print("✅ 登出测试通过！")
    return data


def test_invalid_login():
    """测试无效登录"""
    print("\n=== 测试无效登录 ===")
    
    # 使用错误的密码
    login_data = {
        "login_type": "email",
        "identifier": TEST_USER["email"],
        "password": "WrongPassword123",
        "remember_me": False
    }
    
    response = requests.post(
        f"{AUTH_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"无效登录响应状态码: {response.status_code}")
    print(f"无效登录响应内容: {response.text}")
    
    assert response.status_code == 401, f"无效登录应该返回 401 状态码"
    data = response.json()
    assert "detail" in data, "响应中缺少错误详情"
    assert "账号或密码错误" in data["detail"], "错误信息不正确"
    
    print("✅ 无效登录测试通过！")
    return data


def test_invalid_token():
    """测试无效令牌"""
    print("\n=== 测试无效令牌 ===")
    
    # 使用无效的令牌
    response = requests.get(
        f"{AUTH_URL}/me",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token"
        }
    )
    
    print(f"无效令牌响应状态码: {response.status_code}")
    print(f"无效令牌响应内容: {response.text}")
    
    assert response.status_code == 401, f"无效令牌应该返回 401 状态码"
    data = response.json()
    assert "detail" in data, "响应中缺少错误详情"
    
    print("✅ 无效令牌测试通过！")
    return data


if __name__ == "__main__":
    """运行所有测试"""
    print("开始测试认证系统...\n")
    
    try:
        # 1. 测试注册
        registered_user = test_register()
        
        # 2. 测试登录
        login_data = test_login()
        
        # 3. 测试获取当前用户信息
        user_info = test_get_current_user()
        
        # 4. 测试刷新令牌
        refreshed_tokens = test_refresh_token()
        
        # 5. 测试登出
        logout_result = test_logout()
        
        # 6. 测试无效登录
        invalid_login_result = test_invalid_login()
        
        # 7. 测试无效令牌
        invalid_token_result = test_invalid_token()
        
        print("\n" + "="*50)
        print("🎉 所有测试通过！认证系统工作正常。")
        print("="*50)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
