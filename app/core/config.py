from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # 資料庫設定
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # JWT 設定
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 應用設定
    APP_NAME: str = "User Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # 安全設定
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 分頁設定
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 密碼設定
    MIN_PASSWORD_LENGTH: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # 允許額外的欄位
        extra = "ignore"

# 創建設定實例
settings = Settings()

# 開發環境自動載入
if settings.ENVIRONMENT == "development":
    settings.DEBUG = True