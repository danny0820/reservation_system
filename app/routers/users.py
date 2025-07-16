from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from app.database import get_db
from app.core.config import settings
from app.models.user_models import User
from app.schemas.user_schemas import (
    UserCreate, UserSignup, UserUpdate, UserUpdatePassword, 
    UserResponse, UserRoleAssignment, Token, UserStatusUpdate,
    LinkedAccountsResponse, PasswordResetRequest, VerificationRequest
)
from app.auth import (
    authenticate_user, create_access_token, 
    get_current_active_user, get_admin_user, verify_password
)
from app.crud.user_crud import user_crud

router = APIRouter()

@router.post("/login", response_model=Token, summary="用戶登入", description="使用用戶名和密碼進行身份驗證，成功後返回訪問令牌")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=List[UserResponse], summary="獲取所有用戶", description="(管理員權限) 獲取系統中所有用戶的列表")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="創建新用戶", description="(管理員權限) 在系統中創建一個新的用戶帳號")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 檢查用戶名是否已存在
    if user_crud.is_username_taken(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # 檢查電子郵件是否已存在
    if user.email and user_crud.is_email_taken(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return user_crud.create_user(db, user)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="用戶註冊", description="新用戶註冊帳號，預設角色為客戶")
async def signup_user(user: UserSignup, db: Session = Depends(get_db)):
    # 檢查用戶名是否已存在
    if user_crud.is_username_taken(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # 檢查電子郵件是否已存在
    if user.email and user_crud.is_email_taken(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return user_crud.create_customer(
        db=db,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        password=user.password,
        image=user.image
    )

@router.get("/me", response_model=UserResponse, summary="獲取個人資訊", description="獲取當前登入用戶的個人資訊")
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.patch("/me", response_model=UserResponse, summary="更新個人資訊", description="更新當前登入用戶的個人資訊")
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 檢查電子郵件是否已被其他用戶使用
    if user_update.email and user_update.email != current_user.email:
        if user_crud.is_email_taken(db, user_update.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    return user_crud.update_user(db, current_user, user_update)

@router.patch("/me/password", response_model=dict, summary="更新密碼", description="更新當前登入用戶的密碼")
async def update_current_user_password(
    password_update: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not verify_password(password_update.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    user_crud.update_user_password(db, current_user, password_update.new_password)
    return {"message": "Password updated successfully"}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="刪除個人帳號", description="刪除當前登入用戶的帳號")
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_crud.delete_user(db, current_user)

@router.get("/{user_id}", response_model=UserResponse, summary="獲取指定用戶", description="(管理員權限) 根據用戶ID獲取指定用戶的資訊")
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse, summary="更新指定用戶", description="(管理員權限) 根據用戶ID更新指定用戶的資訊")
async def update_user_by_id(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 檢查電子郵件是否已被其他用戶使用
    if user_update.email and user_update.email != user.email:
        if user_crud.is_email_taken(db, user_update.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    return user_crud.update_user(db, user, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="刪除指定用戶", description="(管理員權限) 根據用戶ID刪除指定的用戶")
async def delete_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_crud.delete_user(db, user)

@router.post("/{user_id}/role", response_model=UserResponse, summary="分配用戶角色", description="(管理員權限) 為指定用戶分配新的角色")
async def assign_user_role(
    user_id: str,
    role_assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_crud.update_user_role(db, user, role_assignment.role)

# 角色與狀態查詢 API

@router.get("/role/{role}", response_model=List[UserResponse], summary="獲取指定角色用戶", description="根據角色獲取用戶列表")
async def get_users_by_role(
    role: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    users = user_crud.get_users_by_role(db, role, skip=skip, limit=limit)
    return users

@router.get("/status/{status}", response_model=List[UserResponse], summary="獲取指定狀態用戶", description="根據狀態獲取用戶列表")
async def get_users_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    users = user_crud.get_users_by_status(db, status, skip=skip, limit=limit)
    return users



# 進階用戶管理 API

@router.post("/{user_id}/status", response_model=UserResponse, summary="更改用戶狀態", description="(管理員權限) 更改指定用戶的狀態")
async def change_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_crud.update_user_status(db, user, status_update.status)

@router.post("/{user_id}/activate", response_model=UserResponse, summary="啟用用戶", description="(管理員權限) 啟用指定用戶")
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_crud.update_user_status(db, user, "active")

@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="停用用戶", description="(管理員權限) 停用指定用戶")
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_crud.update_user_status(db, user, "inactive")

# 用戶關係管理 API

@router.get("/{user_id}/linked-accounts", response_model=LinkedAccountsResponse, summary="查看連結的第三方帳號", description="查看指定用戶的第三方帳號連結狀態")
async def get_linked_accounts(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    accounts = user_crud.get_linked_accounts(db, user_id)
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return accounts

@router.post("/{user_id}/send-verification", response_model=dict, summary="發送驗證信", description="為指定用戶發送驗證信")
async def send_verification(
    user_id: str,
    verification_request: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 這裡可以實現實際的驗證信發送邏輯
    # 目前回傳成功訊息
    verification_type = "email" if verification_request.email else "phone"
    return {
        "message": f"Verification {verification_type} sent successfully",
        "user_id": user_id,
        "verification_type": verification_type
    }

@router.post("/{user_id}/reset-password", response_model=dict, summary="重置密碼", description="重置指定用戶的密碼")
async def reset_password(
    user_id: str,
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_crud.reset_user_password(db, user, password_reset.new_password)
    return {
        "message": "Password reset successfully",
        "user_id": user_id
    }