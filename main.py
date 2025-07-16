from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.core.config import settings

# 初始化 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="美髮預約系統的用戶管理 API"
)

# 設定 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 引入使用者路由
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
async def root():
    """
    根目錄，提供 API 基本資訊。

    :return: dict, 包含 API 訊息、版本和環境。
    """
    return {
        "message": "User Management API",
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development"
    }

@app.get("/health")
async def health_check():
    """
    健康檢查端點。

    :return: dict, 包含服務健康狀態。
    """
    return {"status": "healthy"}