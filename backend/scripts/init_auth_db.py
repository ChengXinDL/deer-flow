"""认证数据库初始化脚本"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_base_dir():
    """获取基础目录"""
    if env_home := os.getenv("MAGIC_FLOW_HOME"):
        return Path(env_home).resolve()
    
    cwd = Path.cwd()
    if cwd.name == "backend" or (cwd / "pyproject.toml").exists():
        return cwd / ".magic-flow"
    
    return Path.home() / ".magic-flow"

def main():
    """初始化认证数据库"""
    try:
        logger.info("开始初始化认证数据库...")
        
        # 设置环境变量（强制覆盖）
        os.environ["POSTGRES_URL"] = "postgresql://app_user:Sykj_1234P@192.168.9.174:5432/pg_db"
        
        # 直接导入 SQLAlchemy
        from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey
        from sqlalchemy.sql import func
        from sqlalchemy.orm import declarative_base, relationship
        from sqlalchemy.pool import StaticPool
        from uuid import uuid4
        
        Base = declarative_base()
        
        class User(Base):
            """用户模型"""
            __tablename__ = "users"
            
            id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
            email = Column(String(255), unique=True, nullable=True, index=True)
            phone = Column(String(20), unique=True, nullable=True, index=True)
            password_hash = Column(String(255), nullable=True)
            name = Column(String(255), nullable=False)
            username = Column(String(100), unique=True, nullable=True, index=True)
            avatar_url = Column(String(500), nullable=True)
            
            github_id = Column(String(100), unique=True, nullable=True)
            google_id = Column(String(100), unique=True, nullable=True)
            wechat_openid = Column(String(100), unique=True, nullable=True)
            
            is_active = Column(Boolean, default=True)
            is_verified = Column(Boolean, default=False)
            email_verified_at = Column(DateTime, nullable=True)
            phone_verified_at = Column(DateTime, nullable=True)
            
            created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
            updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
            last_login_at = Column(DateTime, nullable=True)
        
        class RefreshToken(Base):
            """刷新令牌模型"""
            __tablename__ = "refresh_tokens"
            
            id = Column(String(36), primary_key=True)
            user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
            token = Column(String(500), unique=True, nullable=False, index=True)
            expires_at = Column(DateTime, nullable=False)
            is_revoked = Column(Boolean, default=False)
            created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
            revoked_at = Column(DateTime, nullable=True)
        
        class PasswordResetToken(Base):
            """密码重置令牌模型"""
            __tablename__ = "password_reset_tokens"
            
            id = Column(String(36), primary_key=True)
            user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
            token = Column(String(500), unique=True, nullable=False, index=True)
            expires_at = Column(DateTime, nullable=False)
            is_used = Column(Boolean, default=False)
            created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
            used_at = Column(DateTime, nullable=True)
        
        # 获取数据库连接字符串
        DATABASE_URL = os.getenv(
            "POSTGRES_URL",
            os.getenv(
                "AUTH_DATABASE_URL",
                "sqlite:///" + str(get_base_dir() / "auth.db")
            )
        )
        
        logger.info(f"使用数据库: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        
        # 创建数据库引擎
        if "sqlite" in DATABASE_URL:
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            engine = create_engine(
                DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("认证数据库初始化成功！")
        logger.info("数据库表已创建：users, refresh_tokens, password_reset_tokens")
    except Exception as e:
        logger.error(f"认证数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
