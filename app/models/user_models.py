from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    customer = "customer"
    stylist = "stylist"
    admin = "admin"

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(String(36), primary_key=True, index=True)
    stylist_id = Column(String(36), nullable=True)
    image = Column(String(255), nullable=True)
    username = Column(String(100), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    phone = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password = Column(String(255), nullable=True)
    google_uid = Column(String(100), unique=True, nullable=True)
    line_uid = Column(String(100), unique=True, nullable=True)
    status = Column(String(50), nullable=False)
    notification = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())