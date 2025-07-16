from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user_models import UserRole

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: str = Field(..., min_length=1, max_length=30)
    email: Optional[EmailStr] = None
    image: Optional[str] = Field(None, max_length=255)
    notification: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.customer
    status: str = Field(default="active")

class UserSignup(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: str = Field(..., min_length=1, max_length=30)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    image: Optional[str] = Field(None, max_length=255)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, min_length=1, max_length=30)
    email: Optional[EmailStr] = None
    image: Optional[str] = Field(None, max_length=255)
    notification: Optional[str] = Field(None, max_length=50)

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    user_id: str
    role: UserRole
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserRoleAssignment(BaseModel):
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 新增的 Schema 類別

class UserSearchResponse(BaseModel):
    """用戶搜尋結果回應"""
    user_id: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: str
    role: UserRole
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserFilterRequest(BaseModel):
    """用戶篩選條件請求"""
    role: Optional[UserRole] = None
    status: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = 0
    limit: int = 100

class UserStatsResponse(BaseModel):
    """用戶統計資訊回應"""
    total_users: int
    active_users: int
    inactive_users: int
    customers: int
    stylists: int
    admins: int
    new_users_this_month: int
    new_users_today: int

class UserStatusUpdate(BaseModel):
    """用戶狀態更新請求"""
    status: str = Field(..., description="新的用戶狀態")

class LinkedAccountsResponse(BaseModel):
    """第三方帳號連結回應"""
    user_id: str
    google_uid: Optional[str]
    line_uid: Optional[str]
    has_google_account: bool
    has_line_account: bool
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    """密碼重置請求"""
    new_password: str = Field(..., min_length=6, description="新密碼")

class VerificationRequest(BaseModel):
    """驗證請求"""
    email: Optional[str] = None
    phone: Optional[str] = None