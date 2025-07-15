from app.database import create_tables
from app.core.config import settings

def main():
    """創建資料庫表並啟動應用程序"""
    print(f"正在連接到資料庫: {settings.DATABASE_URL}")
    try:
        create_tables()
        print("✅ 資料庫表創建成功")
    except Exception as e:
        print(f"❌ 資料庫表創建失敗: {e}")
        raise

if __name__ == "__main__":
    main()
    print("啟動 API 伺服器...")
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)