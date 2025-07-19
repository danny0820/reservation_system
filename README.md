   # 美髮預約系統 - 管理 API

快速上手指南和 API 使用說明

## 🚀 快速啟動

1. **啟動服務**
   ```bash
   uvicorn main:app --reload --port 8080
   ```

2. **訪問 API 文檔**
   - Swagger UI: http://127.0.0.1:8080/docs
   - ReDoc: http://127.0.0.1:8080/redoc

## 📋 API 快速參考

### 🔐 認證系統
- `POST /users/login` - 用戶登入
- `POST /users/signup` - 用戶註冊

### 👤 個人資料管理
- `GET /users/me` - 獲取個人資訊
- `PATCH /users/me` - 更新個人資訊
- `PATCH /users/me/password` - 更新密碼
- `DELETE /users/me` - 刪除帳號

### 👥 用戶管理功能

#### 🔐 管理員專用
- `GET /users/` - 獲取所有用戶
- `POST /users/` - 創建新用戶
- `GET /users/{user_id}` - 獲取指定用戶
- `PATCH /users/{user_id}` - 更新指定用戶
- `DELETE /users/{user_id}` - 刪除指定用戶
- `POST /users/{user_id}/role` - 分配用戶角色
- `POST /users/{user_id}/status` - 更改用戶狀態
- `POST /users/{user_id}/activate` - 啟用用戶
- `POST /users/{user_id}/deactivate` - 停用用戶

#### 👤 所有已認證用戶可用
- `GET /users/role/{role}` - 獲取指定角色用戶
- `GET /users/status/{status}` - 獲取指定狀態用戶
- `GET /users/{user_id}/linked-accounts` - 查看連結的第三方帳號
- `POST /users/{user_id}/send-verification` - 發送驗證信
- `POST /users/{user_id}/reset-password` - 重置密碼

### 🛍️ 商品管理功能 ✅

#### 📦 所有已認證用戶可用
- `GET /products/` - 獲取所有商品/服務列表
- `GET /products/{product_id}` - 獲取指定商品詳情
- `GET /products/services` - 獲取服務項目列表
- `GET /products/products` - 獲取商品項目列表
- `GET /products/search` - 搜尋商品

#### 🔐 管理員專用
- `POST /products/` - 創建新商品/服務
- `PATCH /products/{product_id}` - 更新商品資訊
- `DELETE /products/{product_id}` - 刪除商品
- `PATCH /products/{product_id}/status` - 更新商品狀態
- `PATCH /products/{product_id}/stock` - 更新庫存
- `PATCH /products/{product_id}/price` - 更新價格

### 📅 排程管理功能 ✅

#### 💇‍♀️ 設計師排班管理
- `GET /schedules/stylists/{stylist_id}` - 獲取設計師排班
- `POST /schedules/stylists/{stylist_id}` - 創建設計師排班
- `PATCH /schedules/schedules/{schedule_id}` - 更新排班
- `DELETE /schedules/schedules/{schedule_id}` - 刪除排班
- `GET /schedules/stylists/{stylist_id}/weekly` - 獲取週排班

#### 🏖️ 請假管理
- `GET /schedules/stylists/{stylist_id}/time-off` - 獲取請假記錄
- `POST /schedules/stylists/{stylist_id}/time-off` - 申請請假
- `PATCH /schedules/time-off/{time_off_id}` - 更新請假申請
- `DELETE /schedules/time-off/{time_off_id}` - 刪除請假申請
- `POST /schedules/time-off/{time_off_id}/approve` - 批准請假
- `POST /schedules/time-off/{time_off_id}/reject` - 拒絕請假

#### 🔍 可用性查詢
- `GET /schedules/stylists/{stylist_id}/availability` - 檢查設計師可用性
- `GET /schedules/stylists/{stylist_id}/conflicts` - 查找排班衝突

### 🏪 門店管理功能 ✅

#### ⏰ 營業時間管理
- `GET /store/business-hours` - 獲取營業時間
- `POST /store/business-hours` - 設定營業時間
- `PATCH /store/business-hours/{day_of_week}` - 更新營業時間
- `DELETE /store/business-hours/{day_of_week}` - 刪除營業時間

#### 🔒 休業管理
- `GET /store/closures` - 獲取休業記錄
- `POST /store/closures` - 創建休業記錄
- `PATCH /store/closures/{closure_id}` - 更新休業記錄
- `DELETE /store/closures/{closure_id}` - 刪除休業記錄

#### 📊 狀態查詢
- `GET /store/status` - 獲取門店當前狀態
- `GET /store/status/{date}` - 獲取指定日期門店狀態

## 🔑 默認管理員帳號

- **用戶名**: admin
- **密碼**: admin123
- **角色**: admin

## 📊 開發進度

### ✅ 已完成並部署
- [x] 用戶認證系統
- [x] 用戶管理功能
- [x] 管理員功能
- [x] 角色查詢 API
- [x] 進階管理 API
- [x] 用戶關係管理
- [x] 分層權限控制
- [x] CRUD 架構
- [x] 安全性配置
- [x] API 文檔
- [x] 單元測試 (88% 覆蓋率)
- [x] 商品/服務管理模組
- [x] 商品庫存管理
- [x] 商品搜尋功能

### ✅ 已完成並部署
- [x] 設計師排班管理模組
- [x] 設計師請假系統
- [x] 排班衝突檢測
- [x] 設計師可用性查詢
- [x] 門店營業時間管理
- [x] 門店休業管理
- [x] 門店狀態查詢

### 📋 待開發功能
- [ ] 客戶預約模組
- [ ] 預約衝突檢測
- [ ] 預約通知系統
- [ ] 服務記錄管理
- [ ] 客戶服務歷史
- [ ] 收入統計報表
- [ ] 設計師績效統計
- [ ] 門店分析報表

## 🛠️ 技術棧

- **框架**: FastAPI
- **資料庫**: MySQL (Zeabur)
- **ORM**: SQLAlchemy
- **認證**: JWT
- **驗證**: Pydantic
- **測試**: Pytest

## 📁 項目結構

```
app/
├── core/config.py              # 配置管理
├── crud/                       # CRUD 操作層
│   ├── user_crud.py           # 用戶 CRUD
│   ├── product_crud.py        # 商品 CRUD
│   ├── schedule_crud.py       # 排程 CRUD
│   └── store_crud.py          # 門店 CRUD
├── models/                     # 資料庫模型
│   ├── user_models.py         # 用戶模型
│   ├── product_models.py      # 商品模型
│   ├── schedule_models.py     # 排程模型
│   └── store_models.py        # 門店模型
├── routers/                    # API 路由
│   ├── users.py               # 用戶路由
│   ├── products.py            # 商品路由
│   ├── schedules.py           # 排程路由 ✅
│   └── store.py               # 門店路由 ✅
├── schemas/                    # Pydantic 模型
│   ├── user_schemas.py        # 用戶驗證模型
│   ├── product_schemas.py     # 商品驗證模型
│   ├── schedule_schemas.py    # 排程驗證模型
│   └── store_schemas.py       # 門店驗證模型
├── auth.py                     # 認證系統
└── database.py                 # 資料庫連接
```

## 🏗️ 系統架構

### 🎯 模組狀態
1. **用戶管理模組** ✅ - 完整的用戶認證、權限控制、個人資料管理
2. **商品管理模組** ✅ - 商品和服務項目的完整 CRUD，庫存管理
3. **排程管理模組** ✅ - 設計師排班、請假、可用性管理
4. **門店管理模組** ✅ - 營業時間、休業管理、狀態查詢

### 🔐 權限分層架構
1. **管理員 (admin)**: 所有功能的完整管理權限
2. **設計師 (stylist)**: 個人排班管理、請假申請、商品查詢
3. **客戶 (customer)**: 商品查詢、個人資料管理
4. **未認證用戶**: 僅可註冊和登入

### 🗃️ 資料庫設計
- **Users** - 用戶基本資訊和角色
- **Products** - 商品和服務項目
- **StylistSchedules** - 設計師排班記錄
- **StylistTimeOff** - 設計師請假記錄
- **StoreBusinessHours** - 門店營業時間
- **StoreClosures** - 門店休業記錄

---

**版本**: 2.1.1  
**狀態**: 生產就緒  
**最後更新**: 2025-07-19

### 🔄 最新更新 (v2.1.1)

#### 🛠️ 修復問題
- **資料庫結構修復**: 修復 StoreClosures 表缺少 created_at 和 updated_at 欄位的問題
- **營業時間驗證邏輯**: 修復公休日設定時無法輸入時間但時間又是必填的驗證邏輯問題
- **API 回應驗證**: 修復門店營業時間查詢時的回應驗證錯誤

#### ✅ 新增功能 (v2.1.0)
- **商品管理系統**: 完整的商品和服務項目管理
- **庫存管理**: 商品庫存追蹤和更新
- **價格管理**: 動態價格調整功能
- **搜尋功能**: 強化的商品搜尋和篩選
- **排程管理**: 設計師排班和請假系統 ✅ 已部署
- **門店管理**: 營業時間和休業管理 ✅ 已部署

#### ✅ 系統完善
- 所有四個核心模組完整部署
- 完整的 API 端點覆蓋
- 統一的權限控制系統
- 完善的錯誤處理和驗證
- 資料庫表結構完整性驗證

### 🎯 下一步開發計劃
1. **開發預約管理系統** - 客戶預約核心功能
2. **建立統計報表系統** - 營收和績效分析
3. **優化用戶體驗** - 前端界面和流程改善
4. **擴展通知系統** - 郵件和訊息推送功能