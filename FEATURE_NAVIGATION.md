# 功能導航 - 使用者管理 API

> 本檔案記錄專案中已實現的所有類別、方法和功能，方便快速了解現有功能

---

## 📂 專案結構概覽

```
app/
├── models/         # 資料庫模型
├── schemas/        # Pydantic 資料驗證模型
├── crud/          # 資料庫操作
├── routers/       # API 路由
├── auth.py        # 認證相關功能
├── database.py    # 資料庫配置
└── core/
    └── config.py  # 應用程式配置
```

---

## 📋 已實現功能清單

### 🗄️ 資料庫模型 (`app/models/user_models.py`)

#### `UserRole` (枚舉類)
- **用途**: 定義使用者角色類型
- **可用角色**:
  - `customer`: 客戶
  - `stylist`: 設計師
  - `admin`: 管理員

#### `User` (資料庫模型)
- **用途**: 使用者資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `user_id`: 使用者唯一識別碼
  - `username`: 使用者名稱
  - `first_name`, `last_name`: 姓名
  - `role`: 使用者角色
  - `phone`: 電話號碼
  - `email`: 電子郵件
  - `password`: 密碼（哈希）
  - `google_uid`, `line_uid`: 第三方登入識別碼
  - `status`: 使用者狀態
  - `created_at`, `updated_at`: 時間戳記

---

### 📝 資料驗證架構 (`app/schemas/user_schemas.py`)

#### `UserBase` (基礎模型)
- **用途**: 使用者基本資料欄位

#### `UserCreate` (建立使用者)
- **用途**: 建立新使用者時的資料驗證
- **繼承**: `UserBase`
- **額外欄位**: `password`, `role`, `status`

#### `UserSignup` (使用者註冊)
- **用途**: 使用者自行註冊時的資料驗證
- **特點**: 簡化版的使用者建立表單

#### `UserUpdate` (更新使用者)
- **用途**: 更新使用者資料時的驗證
- **特點**: 所有欄位都是可選的

#### `UserUpdatePassword` (密碼更新)
- **用途**: 更新密碼專用模型
- **欄位**: `current_password`, `new_password`

#### `UserResponse` (回應模型)
- **用途**: API 回應時的使用者資料格式
- **繼承**: `UserBase`
- **額外欄位**: `user_id`, `role`, `status`, `created_at`, `updated_at`

#### `UserRoleAssignment` (角色分配)
- **用途**: 管理員分配使用者角色
- **欄位**: `role`

#### `Token` & `TokenData` (令牌相關)
- **用途**: JWT 令牌相關的資料模型

#### `UserStatusUpdate` (狀態更新)
- **用途**: 更新用戶狀態的請求模型
- **欄位**: `status`

#### `LinkedAccountsResponse` (連結帳號回應)
- **用途**: 第三方帳號連結狀態的回應格式
- **功能**: 顯示 Google、LINE 等第三方帳號連結情況

#### `VerificationRequest` (驗證請求)
- **用途**: 發送驗證信的請求模型
- **欄位**: `email`, `phone`

#### `PasswordResetRequest` (密碼重置請求)
- **用途**: 重置密碼的請求模型
- **欄位**: `new_password`

---

### 🔧 CRUD 操作 (`app/crud/user_crud.py`)

#### `UserCRUD` 類
完整的使用者資料庫操作類，提供以下方法：

##### 查詢操作
- `get_user_by_id(db, user_id)`: 根據 ID 獲取使用者
- `get_user_by_username(db, username)`: 根據使用者名稱獲取使用者
- `get_user_by_email(db, email)`: 根據電子郵件獲取使用者
- `get_users(db, skip, limit)`: 獲取使用者列表（分頁）

##### 建立操作
- `create_user(db, user)`: 建立新使用者（通用）
- `create_customer(db, ...)`: 建立客戶使用者（特化）

##### 更新操作
- `update_user(db, user, user_update)`: 更新使用者資訊
- `update_user_password(db, user, new_password)`: 更新使用者密碼
- `update_user_role(db, user, new_role)`: 更新使用者角色

##### 刪除操作
- `delete_user(db, user)`: 刪除使用者

##### 驗證操作
- `is_username_taken(db, username)`: 檢查使用者名稱是否已使用
- `is_email_taken(db, email)`: 檢查電子郵件是否已使用

##### 進階查詢操作
- `get_users_by_role(db, role, skip, limit)`: 根據角色獲取用戶列表
- `get_users_by_status(db, status, skip, limit)`: 根據狀態獲取用戶列表

##### 進階管理操作
- `update_user_status(db, user, status)`: 更新用戶狀態
- `reset_user_password(db, user, new_password)`: 重置用戶密碼
- `get_linked_accounts(db, user_id)`: 獲取第三方帳號連結狀態

**單例實例**: `user_crud` - 可直接使用的 UserCRUD 實例

---

### 🛣️ API 路由 (`app/routers/users.py`)

#### 認證路由（無需認證）
- `POST /login`: 使用者登入，返回 JWT 令牌
- `POST /signup`: 使用者註冊

#### 個人資料路由（需要認證）
- `GET /me`: 獲取個人資訊
- `PATCH /me`: 更新個人資訊
- `PATCH /me/password`: 更新個人密碼
- `DELETE /me`: 刪除個人帳號

#### 使用者管理路由（管理員權限）
- `GET /`: 獲取所有使用者列表
- `POST /`: 建立新使用者
- `GET /{user_id}`: 根據 ID 獲取指定使用者
- `PATCH /{user_id}`: 更新指定使用者資訊
- `DELETE /{user_id}`: 刪除指定使用者
- `POST /{user_id}/role`: 分配使用者角色
- `POST /{user_id}/status`: 更改用戶狀態
- `POST /{user_id}/activate`: 啟用用戶
- `POST /{user_id}/deactivate`: 停用用戶

#### 角色與狀態查詢 API（已認證用戶可用）
- `GET /role/{role}`: 獲取指定角色用戶
- `GET /status/{status}`: 獲取指定狀態用戶

#### 用戶關係管理 API（已認證用戶可用）
- `GET /{user_id}/linked-accounts`: 查看連結的第三方帳號
- `POST /{user_id}/send-verification`: 發送驗證信
- `POST /{user_id}/reset-password`: 重置密碼

---

### 🔐 認證與安全 (`app/auth.py`)

#### 密碼處理
- `verify_password(plain_password, hashed_password)`: 驗證密碼
- `get_password_hash(password)`: 密碼哈希加密

#### 使用者驗證
- `get_user(db, username)`: 根據使用者名稱獲取使用者
- `authenticate_user(db, username, password)`: 驗證使用者身份

#### JWT 令牌
- `create_access_token(data, expires_delta)`: 建立 JWT 訪問令牌

#### 依賴項函數
- `get_current_user(token, db)`: 從令牌獲取當前使用者
- `get_current_active_user(current_user)`: 獲取當前活躍使用者
- `get_admin_user(current_user)`: 獲取管理員使用者（權限檢查）

#### 全域配置
- `pwd_context`: 密碼加密上下文
- `oauth2_scheme`: OAuth2 Bearer 認證方案

---

### ⚙️ 應用程式配置 (`app/core/config.py`)

#### `Settings` 類
應用程式的組態設定類，包含：

##### 資料庫設定
- `DATABASE_URL`: 資料庫連接 URL

##### JWT 設定
- `SECRET_KEY`: JWT 金鑰
- `ALGORITHM`: 加密演算法
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 令牌過期時間

##### 應用設定
- `APP_NAME`: 應用程式名稱
- `APP_VERSION`: 版本號
- `DEBUG`: 除錯模式
- `ENVIRONMENT`: 運行環境

##### 安全設定
- `ALLOWED_HOSTS`: 允許的主機列表

##### 分頁設定
- `DEFAULT_PAGE_SIZE`: 預設分頁大小
- `MAX_PAGE_SIZE`: 最大分頁大小

##### 密碼設定
- `MIN_PASSWORD_LENGTH`: 最小密碼長度

**全域實例**: `settings` - 可直接使用的設定實例

---

### 🗃️ 資料庫配置 (`app/database.py`)

#### 核心功能
- `engine`: SQLAlchemy 資料庫引擎
- `SessionLocal`: 資料庫會話工廠
- `Base`: SQLAlchemy 基礎模型類

#### 函數
- `get_db()`: 資料庫會話依賴項（產生器）
- `create_tables()`: 建立資料庫中的所有表

#### 環境支援
- 支援測試環境（SQLite）和生產環境資料庫切換

---

### 🚀 主應用程式 (`main.py`)

#### `app` (FastAPI 實例)
主要的 FastAPI 應用程式實例

#### 功能配置
- **CORS 中間件**: 跨域請求支援
- **路由註冊**: 使用者相關路由 (`/users`)
- **標籤管理**: API 文件分組

#### 基礎端點
- `GET /`: 根目錄，API 基本資訊
- `GET /health`: 健康檢查端點

---

## 🎯 快速使用指南

### 檢查功能是否存在
1. **使用者管理**: 查看 `UserCRUD` 類的方法
2. **API 端點**: 查看 `app/routers/users.py` 的路由
3. **資料驗證**: 查看 `app/schemas/user_schemas.py` 的模型
4. **認證功能**: 查看 `app/auth.py` 的函數

### 新增功能前的檢查清單
- [ ] 檢查 `UserCRUD` 是否已有相關的資料庫操作方法
- [ ] 檢查是否已有相應的 Pydantic 驗證模型
- [ ] 檢查路由是否已存在類似的端點
- [ ] 檢查認證/授權是否滿足需求

---

## 📊 功能統計

- **資料庫模型**: 1 個主要模型 + 1 個枚舉
- **資料驗證模型**: 11 個 Pydantic 模型
- **CRUD 方法**: 16 個資料庫操作方法
- **API 端點**: 19 個 REST API 端點
- **認證函數**: 7 個認證相關函數
- **配置項目**: 13 個應用程式設定

### 🎯 API 端點分類統計
- **認證相關**: 2 個端點
- **個人資料**: 4 個端點
- **管理員專用**: 9 個端點
- **已認證用戶**: 4 個端點

### 🔐 權限層級說明
1. **無需認證**: 註冊、登入
2. **需要認證**: 個人資料管理、查詢功能
3. **管理員權限**: 系統管理、用戶管理、統計資訊

---

*最後更新: 2025-07-16 - 移除非必要API端點，簡化系統架構*
*維護者: 開發團隊*

---

## 🔄 更新日誌

### v1.2.0 (2025-07-16)
- ✅ 移除非必要的 API 端點 (stylists, customers, admins, search, filter, stats)
- ✅ 清理相關的 CRUD 方法和 Schema 模型
- ✅ 簡化系統架構，保留核心功能
- ✅ 更新文檔和功能導航

### v1.1.0 (2025-07-16)
- ✅ 新增 14 個 API 端點
- ✅ 實現三層權限控制系統
- ✅ 新增角色與狀態查詢功能
- ✅ 新增用戶搜尋與篩選功能
- ✅ 新增進階用戶管理功能
- ✅ 新增用戶關係管理功能
- ✅ 優化權限分配和安全性
- ✅ 更新文檔和功能導航

### v1.0.0 (2024-07-15)
- ✅ 初始版本發布
- ✅ 基礎用戶管理系統
- ✅ JWT 認證機制
- ✅ CRUD 架構建立 