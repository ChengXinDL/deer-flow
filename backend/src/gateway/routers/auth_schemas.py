"""认证相关的数据传输对象"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求"""
    login_type: str = Field(..., description="登录类型：phone 或 email")
    identifier: str = Field(..., description="手机号或邮箱")
    password: str = Field(..., min_length=8, description="密码")
    remember_me: bool = Field(default=False, description="是否记住我")

    @field_validator('login_type')
    @classmethod
    def validate_login_type(cls, v):
        if v not in ['phone', 'email']:
            raise ValueError('login_type 必须是 phone 或 email')
        return v


class RegisterRequest(BaseModel):
    """注册请求"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=8, description="密码")
    name: str = Field(..., min_length=1, max_length=255, description="用户名")

    @model_validator(mode='after')
    def validate_identifier(self):
        if not self.email and not self.phone:
            raise ValueError('邮箱和手机号至少需要提供一个')
        return self


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")
    user_name: Optional[str] = Field(None, description="用户名")
    user_avatar: Optional[str] = Field(None, description="用户头像URL")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    identifier: str = Field(..., description="邮箱或手机号")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: Optional[str]
    phone: Optional[str]
    name: str
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应"""
    message: str
