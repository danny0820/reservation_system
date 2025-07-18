"""測試配置文件"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 設定測試環境
os.environ["TESTING"] = "1"

from main import app
from app.database import get_db, Base
from app.auth import get_current_active_user, get_admin_user
from app.models.user_models import User, UserRole

# 創建測試資料庫
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆寫資料庫依賴"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def create_test_user():
    """創建測試用戶"""
    from datetime import datetime
    user = User()
    user.user_id = "test-user-id"
    user.username = "testuser"
    user.role = UserRole.customer
    user.phone = "1234567890"
    user.email = "test@example.com"
    user.status = "active"
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    return user


def create_test_admin():
    """創建測試管理員"""
    from datetime import datetime
    admin = User()
    admin.user_id = "test-admin-id"
    admin.username = "testadmin"
    admin.role = UserRole.admin
    admin.phone = "1234567890"
    admin.email = "admin@example.com"
    admin.status = "active"
    admin.created_at = datetime.utcnow()
    admin.updated_at = datetime.utcnow()
    return admin


def create_test_stylist():
    """創建測試設計師"""
    from datetime import datetime
    stylist = User()
    stylist.user_id = "test-stylist-id"
    stylist.username = "teststylist"
    stylist.role = UserRole.stylist
    stylist.phone = "1234567890"
    stylist.email = "stylist@example.com"
    stylist.status = "active"
    stylist.created_at = datetime.utcnow()
    stylist.updated_at = datetime.utcnow()
    return stylist


@pytest.fixture
def db():
    """資料庫 fixture"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """測試客戶端 fixture"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(db):
    """認證客戶端 fixture"""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = create_test_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(db):
    """管理員客戶端 fixture"""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = create_test_admin
    app.dependency_overrides[get_admin_user] = create_test_admin
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def stylist_client(db):
    """設計師客戶端 fixture"""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = create_test_stylist
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()