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