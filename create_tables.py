from app.database import create_tables
from app.core.config import settings
# 匯入所有模型以確保表能被正確創建
from app.models import user_models, product_models, schedule_models, store_models

def main():
    """
    主要函式，用於創建資料庫表。
    連接到資料庫並調用 create_tables() 來初始化表結構。
    """
    print(f"正在連接到資料庫: {settings.DATABASE_URL}")
    try:
        create_tables()
        print("資料庫表創建成功")
    except Exception as e:
        print(f"資料庫表創建失敗: {e}")
        raise

if __name__ == "__main__":
    main()
    # print("啟動 API 伺服器...")
    # import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)