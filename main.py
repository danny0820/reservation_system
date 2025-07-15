from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="美髮預約系統的用戶管理 API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": "User Management API",
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}