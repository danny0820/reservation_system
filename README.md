# 美髮預約系統 - 用戶管理 API

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

### 認證
- `POST /users/login` - 用戶登入
- `POST /users/signup` - 用戶註冊

### 個人資料
- `GET /users/me` - 獲取個人資訊
- `PATCH /users/me` - 更新個人資訊
- `PATCH /users/me/password` - 更新密碼
- `DELETE /users/me` - 刪除帳號

### 管理員功能
- `GET /users/` - 獲取所有用戶
- `POST /users/` - 創建新用戶
- `GET /users/{user_id}` - 獲取指定用戶
- `PATCH /users/{user_id}` - 更新指定用戶
- `DELETE /users/{user_id}` - 刪除指定用戶
- `POST /users/{user_id}/role` - 分配用戶角色

## 🔑 默認管理員帳號

- **用戶名**: admin
- **密碼**: admin123
- **角色**: admin

## 📊 開發進度

- [x] 用戶認證系統
- [x] 用戶管理功能
- [x] 管理員功能
- [x] CRUD 架構
- [x] 安全性配置
- [x] API 文檔
- [x] 單元測試 (88% 覆蓋率)
- [ ] 預約管理模組
- [ ] 服務管理模組
- [ ] 排班管理模組
- [ ] 訂單管理模組

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
├── core/config.py         # 配置管理
├── crud/user_crud.py      # 用戶 CRUD 操作
├── models/user_models.py  # 資料庫模型
├── routers/users.py       # 用戶路由
├── schemas/user_schemas.py # Pydantic 模型
├── auth.py                # 認證系統
└── database.py            # 資料庫連接
```

---

**版本**: 1.0.0  
**狀態**: 生產就緒  
**最後更新**: 2024-07-15