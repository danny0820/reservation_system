from sqlalchemy.orm import Session
from sqlalchemy import func, or_, extract
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.user_models import User
from app.schemas.user_schemas import UserCreate, UserUpdate, UserFilterRequest
from app.auth import get_password_hash
import uuid

class UserCRUD:
    """
    使用者資料的 CRUD (建立、讀取、更新、刪除) 操作。
    """
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        根據使用者 ID 獲取使用者。

        :param db: Session, 資料庫會話。
        :param user_id: str, 使用者 ID。
        :return: Optional[User], 找到的使用者或 None。
        """
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        根據使用者名稱獲取使用者。

        :param db: Session, 資料庫會話。
        :param username: str, 使用者名稱。
        :return: Optional[User], 找到的使用者或 None。
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        根據電子郵件獲取使用者。

        :param db: Session, 資料庫會話。
        :param email: str, 電子郵件。
        :return: Optional[User], 找到的使用者或 None。
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        獲取使用者列表（分頁）。

        :param db: Session, 資料庫會話。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :return: List[User], 使用者列表。
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, db: Session, user: UserCreate) -> User:
        """
        創建新使用者。

        :param db: Session, 資料庫會話。
        :param user: UserCreate, 要創建的使用者數據。
        :return: User, 創建的使用者。
        """
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
        """
        創建客戶使用者。

        :param db: Session, 資料庫會話。
        :param username: str, 使用者名稱。
        :param first_name: Optional[str], 名字。
        :param last_name: Optional[str], 姓氏。
        :param phone: str, 電話。
        :param email: Optional[str], 電子郵件。
        :param password: str, 密碼。
        :param image: Optional[str], 圖片 URL。
        :return: User, 創建的客戶使用者。
        """
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
        """
        更新使用者資訊。

        :param db: Session, 資料庫會話。
        :param user: User, 要更新的使用者。
        :param user_update: UserUpdate, 更新的數據。
        :return: User, 更新後的使用者。
        """
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_password(self, db: Session, user: User, new_password: str) -> User:
        """
        更新使用者密碼。

        :param db: Session, 資料庫會話。
        :param user: User, 要更新的使用者。
        :param new_password: str, 新密碼。
        :return: User, 更新後的使用者。
        """
        user.password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_role(self, db: Session, user: User, new_role: str) -> User:
        """
        更新使用者角色。

        :param db: Session, 資料庫會話。
        :param user: User, 要更新的使用者。
        :param new_role: str, 新角色。
        :return: User, 更新後的使用者。
        """
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
    
    def delete_user(self, db: Session, user: User) -> bool:
        """
        刪除使用者。

        :param db: Session, 資料庫會話。
        :param user: User, 要刪除的使用者。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(user)
        db.commit()
        return True
    
    def is_username_taken(self, db: Session, username: str) -> bool:
        """
        檢查使用者名稱是否已被使用。

        :param db: Session, 資料庫會話。
        :param username: str, 使用者名稱。
        :return: bool, 如果已使用返回 True，否則返回 False。
        """
        return db.query(User).filter(User.username == username).first() is not None
    
    def is_email_taken(self, db: Session, email: str) -> bool:
        """
        檢查電子郵件是否已被使用。

        :param db: Session, 資料庫會話。
        :param email: str, 電子郵件。
        :return: bool, 如果已使用返回 True，否則返回 False。
        """
        return db.query(User).filter(User.email == email).first() is not None

    # 新增的 CRUD 方法

    def get_users_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        根據角色查詢用戶。

        :param db: Session, 資料庫會話。
        :param role: str, 用戶角色。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :return: List[User], 指定角色的用戶列表。
        """
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    def get_users_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        根據狀態查詢用戶。

        :param db: Session, 資料庫會話。
        :param status: str, 用戶狀態。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :return: List[User], 指定狀態的用戶列表。
        """
        return db.query(User).filter(User.status == status).offset(skip).limit(limit).all()

    def search_users(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        關鍵字搜尋用戶。

        :param db: Session, 資料庫會話。
        :param keyword: str, 搜尋關鍵字。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :return: List[User], 搜尋結果用戶列表。
        """
        search_filter = or_(
            User.username.ilike(f"%{keyword}%"),
            User.first_name.ilike(f"%{keyword}%"),
            User.last_name.ilike(f"%{keyword}%"),
            User.email.ilike(f"%{keyword}%"),
            User.phone.ilike(f"%{keyword}%")
        )
        return db.query(User).filter(search_filter).offset(skip).limit(limit).all()

    def filter_users(self, db: Session, filter_request: UserFilterRequest) -> List[User]:
        """
        多條件篩選用戶。

        :param db: Session, 資料庫會話。
        :param filter_request: UserFilterRequest, 篩選條件。
        :return: List[User], 篩選結果用戶列表。
        """
        query = db.query(User)
        
        if filter_request.role:
            query = query.filter(User.role == filter_request.role)
        
        if filter_request.status:
            query = query.filter(User.status == filter_request.status)
        
        if filter_request.created_after:
            query = query.filter(User.created_at >= filter_request.created_after)
        
        if filter_request.created_before:
            query = query.filter(User.created_at <= filter_request.created_before)
        
        return query.offset(filter_request.skip).limit(filter_request.limit).all()

    def get_user_stats(self, db: Session) -> dict:
        """
        獲取用戶統計資訊。

        :param db: Session, 資料庫會話。
        :return: dict, 用戶統計數據。
        """
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.status == "active").count()
        inactive_users = db.query(User).filter(User.status == "inactive").count()
        customers = db.query(User).filter(User.role == "customer").count()
        stylists = db.query(User).filter(User.role == "stylist").count()
        admins = db.query(User).filter(User.role == "admin").count()
        
        # 計算本月新用戶
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = db.query(User).filter(User.created_at >= current_month_start).count()
        
        # 計算今日新用戶
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = db.query(User).filter(User.created_at >= today_start).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "customers": customers,
            "stylists": stylists,
            "admins": admins,
            "new_users_this_month": new_users_this_month,
            "new_users_today": new_users_today
        }

    def update_user_status(self, db: Session, user: User, new_status: str) -> User:
        """
        更新用戶狀態。

        :param db: Session, 資料庫會話。
        :param user: User, 要更新的用戶。
        :param new_status: str, 新狀態。
        :return: User, 更新後的用戶。
        """
        user.status = new_status
        db.commit()
        db.refresh(user)
        return user

    def get_linked_accounts(self, db: Session, user_id: str) -> dict:
        """
        獲取第三方帳號連結資訊。

        :param db: Session, 資料庫會話。
        :param user_id: str, 用戶ID。
        :return: dict, 第三方帳號連結資訊。
        """
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        return {
            "user_id": user.user_id,
            "google_uid": user.google_uid,
            "line_uid": user.line_uid,
            "has_google_account": user.google_uid is not None,
            "has_line_account": user.line_uid is not None
        }

    def reset_user_password(self, db: Session, user: User, new_password: str) -> User:
        """
        重置用戶密碼（管理員功能）。

        :param db: Session, 資料庫會話。
        :param user: User, 要重置密碼的用戶。
        :param new_password: str, 新密碼。
        :return: User, 更新後的用戶。
        """
        user.password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

# 創建 UserCRUD 的單例實例
user_crud = UserCRUD()