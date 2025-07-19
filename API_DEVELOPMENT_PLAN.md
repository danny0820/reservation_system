# AppointmentServices、Order、Order_detail 和 Coupon API 設計計劃

## 系統概述
設計四個新模組的完整 API，遵循現有系統的架構模式：
- AppointmentServices（預約服務關聯）
- Order（訂單管理）
- Order_detail（訂單明細）
- Coupon（優惠券系統）

## 架構設計

### 1. 資料庫模型 (Models)

**a) AppointmentServices 模型**
- 多對多關聯表（預約 ↔ 服務）
- 複合主鍵設計 (appointment_id, product_id)
- 級聯刪除支援

**b) Order 模型**
- 完整訂單資訊
- 狀態管理系統 (pending/confirmed/paid/completed/cancelled)
- 預約關聯（可選）
- 優惠券使用記錄

**c) Order_detail 模型**
- 訂單明細項目
- 商品數量和價格記錄
- 客製化備註

**d) Coupon 模型**
- 優惠券基本資訊
- 折扣類型和數值
- 有效期限管理
- 使用狀態追蹤

### 2. 驗證模型 (Schemas)

**AppointmentServices Schemas:**
- `AppointmentServiceCreate` - 新增服務到預約
- `AppointmentServiceResponse` - 預約服務詳情
- `AppointmentServicesCalculation` - 時間和費用計算

**Order Schemas:**
- `OrderCreate` - 創建訂單（含優惠券）
- `OrderUpdate` - 訂單更新
- `OrderResponse` - 訂單詳情回應
- `OrderStatusUpdate` - 狀態更新
- `OrderSummary` - 訂單摘要

**Order_detail Schemas:**
- `OrderDetailCreate` - 新增訂單項目
- `OrderDetailUpdate` - 更新項目
- `OrderDetailResponse` - 項目詳情

**Coupon Schemas:**
- `CouponCreate` - 創建優惠券
- `CouponUpdate` - 更新優惠券
- `CouponResponse` - 優惠券詳情
- `CouponValidation` - 優惠券驗證
- `CouponUsage` - 使用記錄

### 3. CRUD 層實作

**AppointmentServices CRUD：**
- 新增/移除服務項目到預約
- 查詢預約的所有服務
- 計算預約總時間和費用
- 驗證服務項目有效性

**Order CRUD：**
- 訂單生命週期管理
- 狀態轉換邏輯驗證
- 付款狀態追蹤
- 優惠券應用和驗證
- 訂單金額計算（含折扣）

**Order_detail CRUD：**
- 訂單項目管理
- 庫存檢查和扣減
- 價格計算和驗證
- 項目數量調整

**Coupon CRUD：**
- 優惠券生命週期管理
- 有效期限檢查
- 使用條件驗證
- 折扣計算邏輯
- 使用次數追蹤

### 4. API 路由設計

**AppointmentServices 路由 (`/appointment-services`)：**
- `GET /appointments/{appointment_id}/services` - 獲取預約服務
- `POST /appointments/{appointment_id}/services` - 新增服務到預約
- `DELETE /appointments/{appointment_id}/services/{product_id}` - 移除服務
- `GET /appointments/{appointment_id}/calculation` - 獲取預約費用計算

**Order 路由 (`/orders`)：**
- `GET /orders/` - 獲取訂單列表（分頁、篩選）
- `POST /orders/` - 創建新訂單（支援優惠券）
- `GET /orders/{order_id}` - 獲取訂單詳情
- `PATCH /orders/{order_id}/status` - 更新訂單狀態
- `GET /orders/user/{user_id}` - 用戶訂單查詢
- `POST /orders/{order_id}/apply-coupon` - 應用優惠券
- `DELETE /orders/{order_id}/coupon` - 移除優惠券

**Order_detail 路由 (`/order-details`)：**
- `GET /orders/{order_id}/details` - 獲取訂單明細
- `POST /orders/{order_id}/details` - 新增訂單項目
- `PATCH /orders/{order_id}/details/{detail_id}` - 更新項目
- `DELETE /orders/{order_id}/details/{detail_id}` - 刪除項目

**Coupon 路由 (`/coupons`)：**
- `GET /coupons/` - 獲取優惠券列表（管理員）
- `POST /coupons/` - 創建新優惠券（管理員）
- `GET /coupons/{coupon_id}` - 獲取優惠券詳情
- `PATCH /coupons/{coupon_id}` - 更新優惠券（管理員）
- `DELETE /coupons/{coupon_id}` - 刪除優惠券（管理員）
- `POST /coupons/validate` - 驗證優惠券有效性
- `GET /coupons/available` - 獲取可用優惠券（用戶）

### 5. 權限控制

**AppointmentServices：**
- 客戶：查看和修改自己的預約服務
- 設計師：查看和修改負責的預約服務
- 管理員：完整權限

**Order：**
- 客戶：創建和查看自己的訂單
- 設計師：查看相關預約的訂單
- 管理員：完整訂單管理權限

**Coupon：**
- 客戶：查看可用優惠券、驗證優惠券
- 設計師：查看優惠券資訊
- 管理員：完整優惠券管理權限

### 6. 業務邏輯亮點

**預約服務管理：**
- 自動計算服務總時間和預估費用
- 服務衝突檢測（時間重疊）
- 設計師可用性驗證

**訂單處理：**
- 預約與訂單的關聯管理
- 優惠券自動應用和驗證
- 庫存管理和商品扣減
- 訂單狀態自動化追蹤

**優惠券系統：**
- 多種折扣類型（百分比、固定金額）
- 有效期限自動檢查
- 使用條件驗證（最低消費、商品類型）
- 使用次數限制管理

### 7. 測試策略 (TDD)

**單元測試：**
- CRUD 操作測試（每個模組）
- 業務邏輯測試（計算、驗證）
- 優惠券邏輯測試
- 狀態轉換測試

**集成測試：**
- API 端點完整流程測試
- 預約→服務→訂單→付款流程
- 優惠券應用完整流程
- 權限控制測試

**覆蓋率目標：88%**

### 8. 文件結構
```
app/models/
├── appointment_models.py
├── order_models.py
└── coupon_models.py

app/schemas/
├── appointment_schemas.py
├── order_schemas.py
└── coupon_schemas.py

app/crud/
├── appointment_crud.py
├── order_crud.py
└── coupon_crud.py

app/routers/
├── appointments.py
├── orders.py
└── coupons.py

tests/unit/
├── test_appointments.py
├── test_orders.py
└── test_coupons.py

tests/integration/
├── test_appointment_order_integration.py
└── test_coupon_integration.py
```

### 9. 實作順序
1. **第一階段**：AppointmentServices 模組
   - 模型 → Schema → CRUD → 路由 → 測試

2. **第二階段**：Coupon 模組
   - 模型 → Schema → CRUD → 路由 → 測試

3. **第三階段**：Order 和 Order_detail 模組
   - 模型 → Schema → CRUD → 路由 → 測試
   - 整合優惠券邏輯

4. **第四階段**：整合測試和優化
   - 集成測試
   - 性能優化
   - 更新主應用註冊路由

### 10. 特殊功能設計

**訂單與預約整合：**
- 從預約自動生成訂單
- 預約服務自動加入訂單明細
- 訂單狀態影響預約狀態

**優惠券高級功能：**
- 批量生成優惠券
- 優惠券使用統計報表
- 自動過期處理
- 特定用戶群組優惠券

此設計提供完整的預約、訂單和優惠券管理功能，支援美髮預約系統的所有商業需求，並保持與現有系統的一致性。

## 開發進度追蹤

### 已完成任務
- ✅ 計劃設計和文檔創建

### 進行中任務
- 🔄 創建 AppointmentServices 資料庫模型

### 待完成任務
- ⏳ 創建 Order 和 Order_detail 資料庫模型
- ⏳ 創建 Coupon 資料庫模型
- ⏳ 設計所有驗證模型 (Schemas)
- ⏳ 實作 CRUD 操作
- ⏳ 建立 API 路由
- ⏳ 撰寫單元測試和集成測試
- ⏳ 系統整合和優化