"""认证相关接口"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from src.gateway.routers.auth_db import get_auth_db
from src.gateway.routers.auth_security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    get_current_active_user,
    generate_secure_token
)
from src.gateway.routers.auth_models import User, PasswordResetToken
from src.gateway.routers.auth_schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: RegisterRequest, db: Session = Depends(get_auth_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 检查手机号是否已存在
    if user_data.phone:
        existing_user = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=str(uuid4()),
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        name=user_data.name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_auth_db)):
    """用户登录"""
    # 根据登录类型查找用户
    if login_data.login_type == "email":
        user = db.query(User).filter(User.email == login_data.identifier).first()
    elif login_data.login_type == "phone":
        user = db.query(User).filter(User.phone == login_data.identifier).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的登录类型"
        )

    # 验证用户和密码
    if not user or not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否活跃
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()

    # 创建访问令牌和刷新令牌
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(user_id=user.id, remember_me=login_data.remember_me, db=db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 60,  # 1小时
        user_name=user.name,
        user_avatar=user.avatar_url
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_auth_db)):
    """刷新访问令牌"""
    # 验证刷新令牌
    refresh_token_obj = verify_refresh_token(refresh_data.refresh_token, db)
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的刷新令牌"
        )

    # 撤销旧的刷新令牌
    refresh_token_obj.is_revoked = True
    db.commit()

    # 获取用户信息
    user = db.query(User).filter(User.id == refresh_token_obj.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 创建新的访问令牌和刷新令牌
    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(user_id=user.id, remember_me=True, db=db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=60 * 60  # 1小时
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_auth_db),
    current_user: User = Depends(get_current_active_user)
):
    """用户登出"""
    # 撤销指定的刷新令牌
    revoke_refresh_token(refresh_data.refresh_token, db)
    
    # 撤销用户的所有刷新令牌
    revoke_all_user_tokens(current_user.id, db)
    
    return MessageResponse(message="登出成功")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_auth_db)):
    """忘记密码"""
    # 根据邮箱或手机号查找用户
    user = None
    if '@' in request.identifier:
        user = db.query(User).filter(User.email == request.identifier).first()
    else:
        user = db.query(User).filter(User.phone == request.identifier).first()
    
    if not user:
        # 为了安全，即使用户不存在也返回成功消息
        return MessageResponse(message="如果账号存在，重置链接已发送")
    
    # 创建密码重置令牌
    token = generate_secure_token()
    expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15分钟过期
    
    reset_token = PasswordResetToken(
        id=generate_secure_token(),
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(reset_token)
    db.commit()
    
    # TODO: 发送邮件或短信（这里需要集成邮件/短信服务）
    # send_password_reset_email(user.email, token)
    
    return MessageResponse(message="如果账号存在，重置链接已发送")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_auth_db)):
    """重置密码"""
    # 查找有效的重置令牌
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request.token,
        PasswordResetToken.used_at == None
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的重置令牌"
        )
    
    # 检查令牌是否过期
    if reset_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌已过期"
        )
    
    # 获取用户
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不存在"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # 标记令牌为已使用
    reset_token.used_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(message="密码重置成功")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_auth_db),
    current_user: User = Depends(get_current_active_user)
):
    """修改密码（已登录用户）"""
    # 验证旧密码
    if not current_user.password_hash or not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="密码修改成功")
