"""OAuth 认证路由"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
import logging
import os

from .auth_db import get_auth_db
from .auth_security import create_access_token, create_refresh_token, generate_secure_token
from .auth_models import User, OAuthAccount, WechatLoginState
from .auth_schemas import (
    OAuthTokenResponse,
    WechatQrCodeResponse,
    WechatStatusResponse
)
from .oauth_utils import (
    generate_oauth_state,
    validate_oauth_state,
    get_github_user_info,
    get_github_user_emails,
    get_google_user_info,
    exchange_github_code_for_token,
    exchange_google_code_for_token
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["OAuth"])


def get_oauth_config():
    """获取 OAuth 配置"""
    return {
        "github": {
            "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8001/api/oauth/github/callback"),
        },
        "google": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/api/oauth/google/callback"),
        },
        "wechat": {
            "app_id": os.getenv("WECHAT_APP_ID", ""),
            "app_secret": os.getenv("WECHAT_APP_SECRET", ""),
            "redirect_uri": os.getenv("WECHAT_REDIRECT_URI", "http://localhost:8001/api/oauth/wechat/callback"),
        }
    }


@router.get("/github/authorize")
async def github_authorize():
    """GitHub 授权入口"""
    config = get_oauth_config()
    
    if not config["github"]["client_id"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth 未配置"
        )
    
    state = generate_oauth_state()
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={config['github']['client_id']}"
        f"&scope=read:user%20user:email"
        f"&state={state}"
        f"&redirect_uri={config['github']['redirect_uri']}"
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_auth_db)
):
    """GitHub 授权回调"""
    try:
        config = get_oauth_config()
        
        if not validate_oauth_state(state):
            logger.warning(f"GitHub 登录: 无效的 state 参数: {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 state 参数"
            )
        
        token_response = await exchange_github_code_for_token(
            code,
            config["github"]["client_id"],
            config["github"]["client_secret"],
            config["github"]["redirect_uri"]
        )
        
        if not token_response or 'access_token' not in token_response:
            logger.error(f"GitHub 授权失败: {token_response}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub 授权失败"
            )
        
        access_token = token_response['access_token']
        
        user_info = await get_github_user_info(access_token)
        if not user_info:
            logger.error("获取 GitHub 用户信息失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取 GitHub 用户信息失败"
            )
        
        github_id = str(user_info.get('id'))
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('login')
        avatar_url = user_info.get('avatar_url')
        
        if not email:
            logger.info(f"GitHub 用户未公开邮箱，尝试获取邮箱列表: github_id={github_id}")
            email = await get_github_user_emails(access_token)
        
        user = db.query(User).filter(User.github_id == github_id).first()
        
        if not user:
            if email:
                user = db.query(User).filter(User.email == email).first()
            
            if not user:
                user = User(
                    id=str(uuid4()),
                    email=email,
                    name=name,
                    avatar_url=avatar_url,
                    github_id=github_id,
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"创建新用户: {user.id}, github_id={github_id}")
            else:
                user.github_id = github_id
                user.avatar_url = avatar_url
                user.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"更新用户 GitHub ID: {user.id}, github_id={github_id}")
        else:
            user.name = name
            user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
            db.commit()
        
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == 'github'
        ).first()
        
        if not oauth_account:
            oauth_account = OAuthAccount(
                id=str(uuid4()),
                user_id=user.id,
                provider='github',
                provider_user_id=github_id,
                access_token=access_token,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(oauth_account)
            db.commit()
        else:
            oauth_account.access_token = access_token
            oauth_account.updated_at = datetime.utcnow()
            db.commit()
        
        jwt_access_token = create_access_token(data={"sub": user.id})
        jwt_refresh_token = create_refresh_token(user_id=user.id, remember_me=True, db=db)
        
        logger.info(f"GitHub 登录成功: user_id={user.id}")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        callback_url = f"{frontend_url}/auth/callback?access_token={jwt_access_token}&refresh_token={jwt_refresh_token}&token_type=bearer&expires_in=3600"
        
        return RedirectResponse(url=callback_url)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub 登录异常: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        error_url = f"{frontend_url}/auth/callback?error=login_failed"
        return RedirectResponse(url=error_url)


@router.get("/wechat/qrcode", response_model=WechatQrCodeResponse)
async def wechat_qrcode(db: Session = Depends(get_auth_db)):
    """获取微信登录二维码"""
    config = get_oauth_config()
    
    state = generate_oauth_state()
    
    wechat_app_id = config["wechat"]["app_id"]
    is_real_app_id = wechat_app_id and not wechat_app_id.startswith("your_")
    
    if not is_real_app_id:
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=wechat_login_{state}"
    else:
        qr_code_url = (
            f"https://open.weixin.qq.com/connect/qrconnect"
            f"?appid={config['wechat']['app_id']}"
            f"&redirect_uri={config['wechat']['redirect_uri']}"
            f"&response_type=code"
            f"&scope=snsapi_login"
            f"&state={state}#wechat_redirect"
        )
    
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    login_state = WechatLoginState(
        id=str(uuid4()),
        state=state,
        qr_code_url=qr_code_url,
        status='pending',
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )
    db.add(login_state)
    db.commit()
    
    return WechatQrCodeResponse(
        qr_code_url=qr_code_url,
        state=state,
        expires_in=300
    )


@router.get("/wechat/status/{state}", response_model=WechatStatusResponse)
async def wechat_status(state: str, db: Session = Depends(get_auth_db)):
    """查询微信登录状态"""
    login_state = db.query(WechatLoginState).filter(
        WechatLoginState.state == state
    ).first()
    
    if not login_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="登录状态不存在"
        )
    
    if login_state.expires_at < datetime.utcnow():
        login_state.status = 'expired'
        db.commit()
    
    user_info = None
    if login_state.status == 'confirmed' and login_state.user_id:
        user = db.query(User).filter(User.id == login_state.user_id).first()
        if user:
            user_info = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.avatar_url
            }
    
    return WechatStatusResponse(
        status=login_state.status,
        user=user_info
    )


@router.get("/wechat/callback", response_model=OAuthTokenResponse)
async def wechat_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_auth_db)
):
    """微信授权回调"""
    login_state = db.query(WechatLoginState).filter(
        WechatLoginState.state == state
    ).first()
    
    if not login_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="登录状态不存在"
        )
    
    wechat_openid = f"mock_openid_{generate_secure_token(16)}"
    wechat_unionid = f"mock_unionid_{generate_secure_token(16)}"
    
    user = db.query(User).filter(User.wechat_openid == wechat_openid).first()
    
    if not user:
        user = User(
            id=str(uuid4()),
            name=f"微信用户{wechat_openid[:8]}",
            wechat_openid=wechat_openid,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login_at = datetime.utcnow()
        db.commit()
    
    login_state.status = 'confirmed'
    login_state.user_id = user.id
    db.commit()
    
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.user_id == user.id,
        OAuthAccount.provider == 'wechat'
    ).first()
    
    if not oauth_account:
        oauth_account = OAuthAccount(
            id=str(uuid4()),
            user_id=user.id,
            provider='wechat',
            provider_user_id=wechat_openid,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(oauth_account)
        db.commit()
    
    jwt_access_token = create_access_token(data={"sub": user.id})
    jwt_refresh_token = create_refresh_token(user_id=user.id, remember_me=True, db=db)
    
    return OAuthTokenResponse(
        access_token=jwt_access_token,
        refresh_token=jwt_refresh_token,
        token_type="bearer",
        expires_in=60 * 60
    )


@router.get("/google/authorize")
async def google_authorize():
    """Google 授权入口"""
    config = get_oauth_config()
    
    if not config["google"]["client_id"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth 未配置"
        )
    
    state = generate_oauth_state()
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={config['google']['client_id']}"
        f"&response_type=code"
        f"&scope=openid%20profile%20email"
        f"&state={state}"
        f"&redirect_uri={config['google']['redirect_uri']}"
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_auth_db)
):
    """Google 授权回调"""
    try:
        config = get_oauth_config()
        
        if not validate_oauth_state(state):
            logger.warning(f"Google 登录: 无效的 state 参数: {state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 state 参数"
            )
        
        token_response = await exchange_google_code_for_token(
            code,
            config["google"]["client_id"],
            config["google"]["client_secret"],
            config["google"]["redirect_uri"]
        )
        
        if not token_response or 'access_token' not in token_response:
            logger.error(f"Google 授权失败: {token_response}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google 授权失败"
            )
        
        access_token = token_response['access_token']
        
        user_info = await get_google_user_info(access_token)
        if not user_info:
            logger.error("获取 Google 用户信息失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取 Google 用户信息失败"
            )
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        avatar_url = user_info.get('picture')
        
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            if email:
                user = db.query(User).filter(User.email == email).first()
            
            if not user:
                user = User(
                    id=str(uuid4()),
                    email=email,
                    name=name,
                    avatar_url=avatar_url,
                    google_id=google_id,
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"创建新用户: {user.id}, google_id={google_id}")
            else:
                user.google_id = google_id
                user.avatar_url = avatar_url
                user.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"更新用户 Google ID: {user.id}, google_id={google_id}")
        else:
            user.name = name
            user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
            db.commit()
        
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == 'google'
        ).first()
        
        if not oauth_account:
            oauth_account = OAuthAccount(
                id=str(uuid4()),
                user_id=user.id,
                provider='google',
                provider_user_id=google_id,
                access_token=access_token,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(oauth_account)
            db.commit()
        else:
            oauth_account.access_token = access_token
            oauth_account.updated_at = datetime.utcnow()
            db.commit()
        
        jwt_access_token = create_access_token(data={"sub": user.id})
        jwt_refresh_token = create_refresh_token(user_id=user.id, remember_me=True, db=db)
        
        logger.info(f"Google 登录成功: user_id={user.id}")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        callback_url = f"{frontend_url}/auth/callback?access_token={jwt_access_token}&refresh_token={jwt_refresh_token}&token_type=bearer&expires_in=3600"
        
        return RedirectResponse(url=callback_url)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google 登录异常: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        error_url = f"{frontend_url}/auth/callback?error=login_failed"
        return RedirectResponse(url=error_url)
