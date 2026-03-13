"""认证数据库会话管理"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.config.paths import get_paths
from src.gateway.routers.auth_models import Base
import os
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 数据库连接字符串
# 直接使用固定的数据库 URL
DATABASE_URL = "postgresql://app_user:Sykj_1234P@192.168.9.174:5432/pg_db"
POSTGRES_URL_FROM_ENV = "手动设置"
AUTH_DATABASE_URL_FROM_ENV = "手动设置"
DEFAULT_POSTGRES_URL = "手动设置"

# 打印数据库连接信息
logger.info(f"=== 认证数据库配置 ===")
logger.info(f"POSTGRES_URL 环境变量: {POSTGRES_URL_FROM_ENV}")
logger.info(f"AUTH_DATABASE_URL 环境变量: {AUTH_DATABASE_URL_FROM_ENV}")
logger.info(f"默认数据库 URL: {DEFAULT_POSTGRES_URL}")
logger.info(f"最终使用的数据库 URL: {DATABASE_URL}")

# 创建数据库引擎
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_auth_db():
    """初始化认证数据库"""
    Base.metadata.create_all(bind=engine)


def get_auth_db() -> Session:
    """获取认证数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
