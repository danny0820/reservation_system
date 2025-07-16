# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 語言設定

**在此專案回應請一律使用中文**

## 常用指令

### 開發與測試
```bash
# 啟動服務
uvicorn main:app --reload --port 8080

# 安裝依賴
pip install -r requirements.txt

# 創建資料庫表
python create_tables.py

# 測試命令（如果有測試文件）
pytest
pytest --cov=app  # 代碼覆蓋率測試
```

### 檢查與格式化
```bash
# 型別檢查
python -m mypy app/

# 代碼格式化
python -m black app/
python -m isort app/

# 代碼檢查
python -m flake8 app/
```

## 系統架構

### 核心架構模式
這是一個基於 **FastAPI** 的美髮預約系統，採用 **分層架構** 設計：

1. **API 層** (`app/routers/`) - 路由和端點定義
2. **業務邏輯層** (`app/crud/`) - 資料庫操作和業務邏輯
3. **資料層** (`app/models/`) - SQLAlchemy 模型定義
4. **驗證層** (`app/schemas/`) - Pydantic 資料驗證
5. **核心服務** (`app/auth.py`, `app/database.py`) - 認證和資料庫服務

### 關鍵設計模式
- **依賴注入**: 使用 FastAPI 的 `Depends` 進行資料庫會話和認證管理
- **CRUD 模式**: 統一的資料庫操作接口 (`UserCRUD` 類)
- **JWT 認證**: 無狀態的使用者認證系統
- **分層權限**: customer → stylist → admin 角色系統

### 資料庫設計
- 使用 SQLAlchemy ORM 與 MySQL 資料庫
- 支援測試環境的 SQLite 切換
- 完整的使用者管理系統（認證、角色、個人資料）
- 為未來模組預留了資料庫結構（預約、訂單、排班、優惠券）

### 功能導航
參考 `FEATURE_NAVIGATION.md` 文件了解：
- 已實現的所有類別和方法
- API 端點的詳細說明
- 資料庫操作的完整清單
- 認證和安全功能

## 重要配置

### 環境變數
核心配置在 `app/core/config.py`：
- `DATABASE_URL`: 資料庫連接字串
- `SECRET_KEY`: JWT 金鑰（生產環境需更改）
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 令牌過期時間
- `ENVIRONMENT`: 運行環境（development/production）

### 安全設定
- 所有密碼使用 bcrypt 哈希
- JWT 令牌用於 API 認證
- 角色基礎的存取控制
- CORS 中間件已配置

### 資料庫環境
- 生產環境：使用 `DATABASE_URL` 設定的 MySQL
- 測試環境：設定 `TESTING=1` 環境變數使用 SQLite
- 開發環境：可在 `config.py` 中調整 `DEBUG` 模式

## 開發重點

### 新增功能前的檢查
1. 確認 `UserCRUD` 類是否已有相關方法
2. 檢查 `app/schemas/user_schemas.py` 是否有對應的驗證模型
3. 查看 `app/routers/users.py` 是否存在類似端點
4. 確認權限需求（customer/stylist/admin）

### 程式碼結構約定
- 所有資料庫操作透過 CRUD 類進行
- API 端點使用 Pydantic 模型進行請求/回應驗證
- 認證使用 `get_current_user` 或 `get_admin_user` 依賴
- 錯誤處理使用 FastAPI 的 `HTTPException`

### 測試策略
- 單元測試覆蓋率目標 88%
- 使用 pytest 和 httpx 進行 API 測試
- 測試環境自動使用 SQLite 資料庫
- 測試檔案應建立在 `tests/` 目錄

## 預定擴展模組

根據 `schema.sql` 和 README，系統規劃包含：
- 預約管理模組 (`Appointments`, `AppointmentServices`)
- 服務/產品管理模組 (`Products`)
- 訂單管理模組 (`Order`, `Order_detail`)
- 排班管理模組 (`StoreBusinessHours`, `StylistSchedules`)
- 優惠券系統 (`coupon`)

新增模組時應遵循現有的架構模式，在對應目錄建立 models, schemas, crud, routers 檔案。