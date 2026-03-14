"""OAuth 相关工具函数"""

import secrets
import string
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import httpx

logger = logging.getLogger(__name__)


def generate_oauth_state() -> str:
    """生成 OAuth state 参数"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def validate_oauth_state(state: str) -> bool:
    """验证 OAuth state 参数"""
    if not state:
        return False
    if len(state) != 32:
        return False
    return all(c in string.ascii_letters + string.digits for c in state)


async def get_github_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """获取 GitHub 用户信息"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        try:
            response = await client.get(
                "https://api.github.com/user",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"获取 GitHub 用户信息失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"获取 GitHub 用户信息异常: {str(e)}")
            return None


async def get_github_user_emails(access_token: str) -> Optional[str]:
    """获取 GitHub 用户邮箱列表"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        try:
            response = await client.get(
                "https://api.github.com/user/emails",
                headers=headers
            )
            if response.status_code == 200:
                emails = response.json()
                verified_emails = [e['email'] for e in emails if e.get('verified') and e.get('primary')]
                return verified_emails[0] if verified_emails else None
            logger.error(f"获取 GitHub 用户邮箱失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"获取 GitHub 用户邮箱异常: {str(e)}")
            return None


async def check_github_organization_membership(access_token: str, organization: str) -> bool:
    """检查用户是否属于指定组织"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        try:
            response = await client.get(
                f"https://api.github.com/user/memberships/orgs/{organization}",
                headers=headers
            )
            return response.status_code == 204
        except Exception as e:
            logger.error(f"检查 GitHub 组织成员异常: {str(e)}")
            return False


async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """获取 Google 用户信息"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"获取 Google 用户信息失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"获取 Google 用户信息异常: {str(e)}")
            return None


async def exchange_github_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
    """使用 GitHub 授权码换取访问令牌"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                },
                headers={
                    "Accept": "application/json"
                }
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"GitHub 授权码换取令牌失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"GitHub 授权码换取令牌异常: {str(e)}")
            return None


async def exchange_google_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
    """使用 Google 授权码换取访问令牌"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Google 授权码换取令牌失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"Google 授权码换取令牌异常: {str(e)}")
            return None


async def refresh_google_token(refresh_token: str, client_id: str, client_secret: str) -> Optional[Dict[str, Any]]:
    """刷新 Google access_token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"刷新 Google 令牌失败: status={response.status_code}, response={response.text}")
            return None
        except Exception as e:
            logger.error(f"刷新 Google 令牌异常: {str(e)}")
            return None
