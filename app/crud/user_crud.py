from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user_models import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.auth import get_password_hash
import uuid

class UserCRUD:
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """根據用戶ID獲取用戶"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """根據用戶名獲取用戶"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """根據電子郵件獲取用戶"""
        return db.query(User).filter(User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取用戶列表"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, db: Session, user: UserCreate) -> User:
        """創建新用戶"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            user_id=str(uuid.uuid4()),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            email=user.email,
            password=hashed_password,
            role=user.role,
            status=user.status,
            image=user.image,
            notification=user.notification
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def create_customer(self, db: Session, username: str, first_name: Optional[str], 
                       last_name: Optional[str], phone: str, email: Optional[str], 
                       password: str, image: Optional[str] = None) -> User:
        """創建客戶用戶"""
        hashed_password = get_password_hash(password)
        db_user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=hashed_password,
            role="customer",
            status="active",
            image=image
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_user(self, db: Session, user: User, user_update: UserUpdate) -> User:
        """更新用戶資訊"""
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_password(self, db: Session, user: User, new_password: str) -> User:
        """更新用戶密碼"""
        user.password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_role(self, db: Session, user: User, new_role: str) -> User:
        """更新用戶角色"""
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
    
    def delete_user(self, db: Session, user: User) -> bool:
        """刪除用戶"""
        db.delete(user)
        db.commit()
        return True
    
    def is_username_taken(self, db: Session, username: str) -> bool:
        """檢查用戶名是否已被使用"""
        return db.query(User).filter(User.username == username).first() is not None
    
    def is_email_taken(self, db: Session, email: str) -> bool:
        """檢查電子郵件是否已被使用"""
        return db.query(User).filter(User.email == email).first() is not None

# 創建單例實例
user_crud = UserCRUD()