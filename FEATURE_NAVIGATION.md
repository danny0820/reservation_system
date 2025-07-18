# 功能導航 - 美髮預約系統 API

> 本檔案記錄專案中已實現的所有類別、方法和功能，方便快速了解現有功能

---

## 📂 專案結構概覽

```
app/
├── models/         # 資料庫模型
│   ├── user_models.py      # 使用者模型
│   ├── product_models.py   # 商品/服務模型
│   ├── schedule_models.py  # 排程模型
│   └── store_models.py     # 門店模型
├── schemas/        # Pydantic 資料驗證模型
│   ├── user_schemas.py     # 使用者驗證模型
│   ├── product_schemas.py  # 商品驗證模型
│   ├── schedule_schemas.py # 排程驗證模型
│   └── store_schemas.py    # 門店驗證模型
├── crud/          # 資料庫操作
│   ├── user_crud.py        # 使用者 CRUD
│   ├── product_crud.py     # 商品 CRUD
│   ├── schedule_crud.py    # 排程 CRUD
│   └── store_crud.py       # 門店 CRUD
├── routers/       # API 路由
│   ├── users.py            # 使用者路由
│   ├── products.py         # 商品路由
│   ├── schedules.py        # 排程路由 (開發中)
│   └── store.py            # 門店路由 (開發中)
├── auth.py        # 認證相關功能
├── database.py    # 資料庫配置
└── core/
    └── config.py  # 應用程式配置
```

---

## 📋 已實現功能清單

### 🗄️ 資料庫模型

#### 使用者模組 (`app/models/user_models.py`)

**`UserRole` (枚舉類)**
- **用途**: 定義使用者角色類型
- **可用角色**:
  - `customer`: 客戶
  - `stylist`: 設計師
  - `admin`: 管理員

**`User` (資料庫模型)**
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

#### 商品模組 (`app/models/product_models.py`)

**`Product` (資料庫模型)**
- **用途**: 商品/服務資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `product_id`: 商品唯一識別碼
  - `name`: 商品/服務名稱
  - `description`: 詳細描述
  - `price`: 價格（以分為單位）
  - `duration_time`: 服務耗時（分鐘）
  - `stock_quantity`: 庫存數量
  - `is_active`: 是否啟用
  - `is_service`: 是否為服務項目
  - `created_at`, `updated_at`: 時間戳記

#### 排程模組 (`app/models/schedule_models.py`)

**`StylistSchedules` (資料庫模型)**
- **用途**: 設計師排班資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `schedule_id`: 排班唯一識別碼
  - `stylist_id`: 設計師 ID（外鍵）
  - `day_of_week`: 星期幾 (0=週日, 1=週一, ..., 6=週六)
  - `start_time`: 開始工作時間
  - `end_time`: 結束工作時間
  - `created_at`, `updated_at`: 時間戳記

**`StylistTimeOff` (資料庫模型)**
- **用途**: 設計師請假資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `time_off_id`: 請假唯一識別碼
  - `stylist_id`: 設計師 ID（外鍵）
  - `start_datetime`: 請假開始時間
  - `end_datetime`: 請假結束時間
  - `reason`: 請假原因
  - `status`: 請假狀態
  - `created_at`, `updated_at`: 時間戳記

#### 門店模組 (`app/models/store_models.py`)

**`StoreBusinessHours` (資料庫模型)**
- **用途**: 店面營業時間資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `hour_id`: 營業時間唯一識別碼
  - `day_of_week`: 星期幾 (0=週日, 1=週一, ..., 6=週六)
  - `open_time`: 開始營業時間
  - `close_time`: 結束營業時間
  - `is_closed`: 當天是否固定公休

**`StoreClosures` (資料庫模型)**
- **用途**: 店面臨時休業資料表對應的 SQLAlchemy 模型
- **主要欄位**:
  - `closure_id`: 休業唯一識別碼
  - `start_datetime`: 休業開始時間
  - `end_datetime`: 休業結束時間
  - `reason`: 休業原因
  - `created_at`, `updated_at`: 時間戳記

---

### 📝 資料驗證架構

#### 使用者模組 (`app/schemas/user_schemas.py`)

- `UserBase`: 使用者基本資料欄位
- `UserCreate`: 建立新使用者時的資料驗證
- `UserSignup`: 使用者自行註冊時的資料驗證
- `UserUpdate`: 更新使用者資料時的驗證
- `UserUpdatePassword`: 密碼更新專用模型
- `UserResponse`: API 回應時的使用者資料格式
- `UserRoleAssignment`: 管理員分配使用者角色
- `Token` & `TokenData`: JWT 令牌相關的資料模型
- `UserStatusUpdate`: 更新用戶狀態的請求模型
- `LinkedAccountsResponse`: 第三方帳號連結狀態的回應格式
- `VerificationRequest`: 發送驗證信的請求模型
- `PasswordResetRequest`: 重置密碼的請求模型

#### 商品模組 (`app/schemas/product_schemas.py`)

- `ProductBase`: 商品基本資料欄位
- `ProductCreate`: 建立新商品時的資料驗證
- `ProductUpdate`: 更新商品資料時的驗證
- `ProductResponse`: API 回應時的商品資料格式
- `ProductStatusUpdate`: 更新商品狀態的請求模型
- `ProductStockUpdate`: 更新庫存的請求模型
- `ProductPriceUpdate`: 更新價格的請求模型

#### 排程模組 (`app/schemas/schedule_schemas.py`)

- `StylistSchedulesBase`: 排班基本資料欄位
- `StylistSchedulesCreate`: 建立新排班的資料驗證
- `StylistSchedulesUpdate`: 更新排班的驗證
- `StylistSchedulesResponse`: 排班回應格式
- `StylistTimeOffBase`: 請假基本資料欄位
- `StylistTimeOffCreate`: 建立請假申請的驗證
- `StylistTimeOffUpdate`: 更新請假的驗證
- `StylistTimeOffResponse`: 請假回應格式
- `TimeOffStatus`: 請假狀態枚舉
- `WeeklyStylistScheduleResponse`: 週排班回應格式
- `StylistAvailabilityResponse`: 設計師可用性回應
- `ScheduleConflictResponse`: 排班衝突回應

#### 門店模組 (`app/schemas/store_schemas.py`)

- `StoreBusinessHoursBase`: 營業時間基本資料欄位
- `StoreBusinessHoursCreate`: 建立營業時間的驗證
- `StoreBusinessHoursUpdate`: 更新營業時間的驗證
- `StoreBusinessHoursResponse`: 營業時間回應格式
- `StoreClosuresBase`: 臨時休業基本資料欄位
- `StoreClosuresCreate`: 建立休業記錄的驗證
- `StoreClosuresUpdate`: 更新休業記錄的驗證
- `StoreClosuresResponse`: 休業記錄回應格式
- `WeeklyBusinessHoursResponse`: 週營業時間回應格式
- `StoreStatusResponse`: 門店狀態回應格式

---

### 🔧 CRUD 操作

#### 使用者 CRUD (`app/crud/user_crud.py`)

**`UserCRUD` 類**
完整的使用者資料庫操作類，提供以下方法：

##### 查詢操作
- `get_user_by_id(db, user_id)`: 根據 ID 獲取使用者
- `get_user_by_username(db, username)`: 根據使用者名稱獲取使用者
- `get_user_by_email(db, email)`: 根據電子郵件獲取使用者
- `get_users(db, skip, limit)`: 獲取使用者列表（分頁）
- `get_users_by_role(db, role, skip, limit)`: 根據角色獲取用戶列表
- `get_users_by_status(db, status, skip, limit)`: 根據狀態獲取用戶列表

##### 建立操作
- `create_user(db, user)`: 建立新使用者（通用）
- `create_customer(db, ...)`: 建立客戶使用者（特化）

##### 更新操作
- `update_user(db, user, user_update)`: 更新使用者資訊
- `update_user_password(db, user, new_password)`: 更新使用者密碼
- `update_user_role(db, user, new_role)`: 更新使用者角色
- `update_user_status(db, user, status)`: 更新用戶狀態

##### 刪除操作
- `delete_user(db, user)`: 刪除使用者

##### 驗證操作
- `is_username_taken(db, username)`: 檢查使用者名稱是否已使用
- `is_email_taken(db, email)`: 檢查電子郵件是否已使用

##### 進階操作
- `reset_user_password(db, user, new_password)`: 重置用戶密碼
- `get_linked_accounts(db, user_id)`: 獲取第三方帳號連結狀態

#### 商品 CRUD (`app/crud/product_crud.py`)

**`ProductCRUD` 類**
完整的商品資料庫操作類，提供以下方法：

##### 查詢操作
- `get_product_by_id(db, product_id)`: 根據 ID 獲取商品
- `get_products(db, skip, limit, is_active)`: 獲取商品列表（分頁）
- `get_products_by_type(db, is_service, skip, limit)`: 根據類型獲取商品
- `search_products(db, query, skip, limit)`: 搜尋商品

##### 建立操作
- `create_product(db, product)`: 建立新商品

##### 更新操作
- `update_product(db, product, product_update)`: 更新商品資訊
- `update_product_status(db, product, is_active)`: 更新商品狀態
- `update_product_stock(db, product, stock_quantity)`: 更新庫存
- `update_product_price(db, product, price)`: 更新價格

##### 刪除操作
- `delete_product(db, product)`: 刪除商品

#### 排程 CRUD (`app/crud/schedule_crud.py`)

**`ScheduleCRUD` 類**
完整的排程資料庫操作類，提供以下方法：

##### 排班操作
- `get_stylist_schedules(db, stylist_id)`: 獲取設計師排班
- `create_stylist_schedule(db, schedule)`: 建立排班
- `update_stylist_schedule(db, schedule, schedule_update)`: 更新排班
- `delete_stylist_schedule(db, schedule)`: 刪除排班

##### 請假操作
- `get_stylist_time_off(db, stylist_id, status)`: 獲取請假記錄
- `create_time_off_request(db, time_off)`: 建立請假申請
- `update_time_off_status(db, time_off, status)`: 更新請假狀態
- `delete_time_off_request(db, time_off)`: 刪除請假申請

##### 可用性檢查
- `check_stylist_availability(db, stylist_id, start_time, end_time)`: 檢查設計師可用性
- `get_weekly_schedule(db, stylist_id)`: 獲取週排班
- `find_schedule_conflicts(db, stylist_id, schedules)`: 查找排班衝突

#### 門店 CRUD (`app/crud/store_crud.py`)

**`StoreCRUD` 類**
完整的門店資料庫操作類，提供以下方法：

##### 營業時間操作
- `get_weekly_business_hours(db)`: 獲取週營業時間
- `create_or_update_business_hours(db, hours)`: 建立或更新營業時間
- `delete_business_hours(db, day_of_week)`: 刪除營業時間

##### 休業管理操作
- `get_store_closures(db, skip, limit)`: 獲取休業記錄
- `create_store_closure(db, closure)`: 建立休業記錄
- `update_store_closure(db, closure, closure_update)`: 更新休業記錄
- `delete_store_closure(db, closure)`: 刪除休業記錄

##### 狀態檢查
- `is_store_open(db, check_datetime)`: 檢查門店是否營業
- `get_store_status(db, check_date)`: 獲取門店狀態

---

### 🛣️ API 路由

#### 使用者路由 (`app/routers/users.py`) ✅ **已部署**

##### 認證路由（無需認證）
- `POST /login`: 使用者登入，返回 JWT 令牌
- `POST /signup`: 使用者註冊

##### 個人資料路由（需要認證）
- `GET /me`: 獲取個人資訊
- `PATCH /me`: 更新個人資訊
- `PATCH /me/password`: 更新個人密碼
- `DELETE /me`: 刪除個人帳號

##### 使用者管理路由（管理員權限）
- `GET /`: 獲取所有使用者列表
- `POST /`: 建立新使用者
- `GET /{user_id}`: 根據 ID 獲取指定使用者
- `PATCH /{user_id}`: 更新指定使用者資訊
- `DELETE /{user_id}`: 刪除指定使用者
- `POST /{user_id}/role`: 分配使用者角色
- `POST /{user_id}/status`: 更改用戶狀態
- `POST /{user_id}/activate`: 啟用用戶
- `POST /{user_id}/deactivate`: 停用用戶

##### 角色與狀態查詢 API（已認證用戶可用）
- `GET /role/{role}`: 獲取指定角色用戶
- `GET /status/{status}`: 獲取指定狀態用戶

##### 用戶關係管理 API（已認證用戶可用）
- `GET /{user_id}/linked-accounts`: 查看連結的第三方帳號
- `POST /{user_id}/send-verification`: 發送驗證信
- `POST /{user_id}/reset-password`: 重置密碼

#### 商品路由 (`app/routers/products.py`) ✅ **已部署**

##### 商品查詢（已認證用戶可用）
- `GET /`: 獲取所有商品/服務列表
- `GET /{product_id}`: 獲取指定商品詳情
- `GET /services`: 獲取服務項目列表
- `GET /products`: 獲取商品項目列表
- `GET /search`: 搜尋商品

##### 商品管理（管理員權限）
- `POST /`: 創建新商品/服務
- `PATCH /{product_id}`: 更新商品資訊
- `DELETE /{product_id}`: 刪除商品
- `PATCH /{product_id}/status`: 更新商品狀態
- `PATCH /{product_id}/stock`: 更新庫存
- `PATCH /{product_id}/price`: 更新價格

#### 排程路由 (`app/routers/schedules.py`) 🚧 **開發中**

##### 設計師排班管理
- `GET /stylists/{stylist_id}`: 獲取設計師排班
- `POST /stylists/{stylist_id}`: 創建設計師排班
- `PATCH /schedules/{schedule_id}`: 更新排班
- `DELETE /schedules/{schedule_id}`: 刪除排班
- `GET /stylists/{stylist_id}/weekly`: 獲取週排班

##### 請假管理
- `GET /stylists/{stylist_id}/time-off`: 獲取請假記錄
- `POST /stylists/{stylist_id}/time-off`: 申請請假
- `PATCH /time-off/{time_off_id}`: 更新請假申請
- `DELETE /time-off/{time_off_id}`: 刪除請假申請
- `POST /time-off/{time_off_id}/approve`: 批准請假
- `POST /time-off/{time_off_id}/reject`: 拒絕請假

##### 可用性查詢
- `GET /stylists/{stylist_id}/availability`: 檢查設計師可用性
- `GET /stylists/{stylist_id}/conflicts`: 查找排班衝突

#### 門店路由 (`app/routers/store.py`) 🚧 **開發中**

##### 營業時間管理
- `GET /business-hours`: 獲取營業時間
- `POST /business-hours`: 設定營業時間
- `PATCH /business-hours/{day_of_week}`: 更新營業時間
- `DELETE /business-hours/{day_of_week}`: 刪除營業時間

##### 休業管理
- `GET /closures`: 獲取休業記錄
- `POST /closures`: 創建休業記錄
- `PATCH /closures/{closure_id}`: 更新休業記錄
- `DELETE /closures/{closure_id}`: 刪除休業記錄

##### 狀態查詢
- `GET /status`: 獲取門店當前狀態
- `GET /status/{date}`: 獲取指定日期門店狀態

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
- **路由註冊**: 
  - 使用者相關路由 (`/users`) ✅
  - 商品相關路由 (`/products`) ✅
  - 排程相關路由 (`/schedules`) 🚧 待註冊
  - 門店相關路由 (`/store`) 🚧 待註冊
- **標籤管理**: API 文件分組

#### 基礎端點
- `GET /`: 根目錄，API 基本資訊
- `GET /health`: 健康檢查端點

---

## 🎯 快速使用指南

### 檢查功能是否存在
1. **使用者管理**: 查看 `UserCRUD` 類的方法
2. **商品管理**: 查看 `ProductCRUD` 類的方法
3. **排程管理**: 查看 `ScheduleCRUD` 類的方法
4. **門店管理**: 查看 `StoreCRUD` 類的方法
5. **API 端點**: 查看各模組路由文件
6. **資料驗證**: 查看各模組 schemas 文件
7. **認證功能**: 查看 `app/auth.py` 的函數

### 新增功能前的檢查清單
- [ ] 檢查相關 CRUD 是否已有相關的資料庫操作方法
- [ ] 檢查是否已有相應的 Pydantic 驗證模型
- [ ] 檢查路由是否已存在類似的端點
- [ ] 檢查主應用程式是否已註冊路由
- [ ] 檢查認證/授權是否滿足需求

---

## 📊 功能統計

### 📈 整體統計
- **資料庫模型**: 6 個主要模型 + 1 個枚舉
- **資料驗證模型**: 35+ 個 Pydantic 模型
- **CRUD 方法**: 50+ 個資料庫操作方法
- **API 端點**: 40+ 個 REST API 端點
- **認證函數**: 7 個認證相關函數
- **配置項目**: 13 個應用程式設定

### 🎯 模組開發狀態
- **使用者管理**: ✅ 完成並部署 (v1.2.0)
- **商品管理**: ✅ 完成並部署 (v2.0.0)
- **排程管理**: 🚧 開發完成，待部署
- **門店管理**: 🚧 開發完成，待部署

### 🔐 權限層級說明
1. **無需認證**: 註冊、登入
2. **需要認證**: 個人資料管理、查詢功能
3. **管理員權限**: 系統管理、用戶管理、商品管理、門店管理
4. **設計師權限**: 個人排班管理、請假申請

---

*最後更新: 2025-07-16 - 新增商品管理、排程管理、門店管理三大模組*
*維護者: 開發團隊*

---

## 🔄 更新日誌

### v2.0.0 (2025-07-16)
- ✅ 新增商品管理模組 (已部署)
  - 商品 CRUD 完整功能
  - 服務項目管理
  - 庫存管理
  - 價格管理
- ✅ 新增排程管理模組 (開發完成)
  - 設計師排班管理
  - 請假申請系統
  - 可用性檢查
  - 衝突檢測
- ✅ 新增門店管理模組 (開發完成)
  - 營業時間管理
  - 休業記錄管理
  - 門店狀態查詢
- ✅ 擴展權限系統支援設計師角色
- ✅ 完善 API 文檔和功能導航

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