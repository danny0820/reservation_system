from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# 根據環境變數決定使用 SQLite 或設定的資料庫
if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)

# 創建資料庫會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建 SQLAlchemy 基礎模型類
Base = declarative_base()

def get_db():
    """
    獲取資料庫會話的依賴項。

    :yield: Session, 資料庫會話。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    創建資料庫中的所有表。
    """
    Base.metadata.create_all(bind=engine)