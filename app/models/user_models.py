from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    """
    使用者角色枚舉。
    """
    customer = "customer"
    stylist = "stylist"
    admin = "admin"

class User(Base):
    """
    使用者資料庫模型。
    對應到資料庫中的 `user` 表。
    """
    __tablename__ = "user"
    
    user_id = Column(String(36), primary_key=True, index=True, comment="使用者 ID")
    stylist_id = Column(String(36), nullable=True, comment="設計師 ID")
    image = Column(String(255), nullable=True, comment="使用者頭像")
    username = Column(String(100), nullable=False, comment="使用者名稱")
    first_name = Column(String(50), nullable=True, comment="名字")
    last_name = Column(String(50), nullable=True, comment="姓氏")
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer, comment="使用者角色")
    phone = Column(String(30), nullable=False, comment="電話號碼")
    email = Column(String(100), unique=True, nullable=True, index=True, comment="電子郵件")
    password = Column(String(255), nullable=True, comment="密碼")
    google_uid = Column(String(100), unique=True, nullable=True, comment="Google UID")
    line_uid = Column(String(100), unique=True, nullable=True, comment="Line UID")
    status = Column(String(50), nullable=False, comment="使用者狀態")
    notification = Column(String(50), nullable=True, comment="通知設定")
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="創建時間")
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新時間")