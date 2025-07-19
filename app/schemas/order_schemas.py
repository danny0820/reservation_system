from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class OrderDetailBase(BaseModel):
    product_id: str = Field(..., description="商品 ID")
    quantity: int = Field(..., ge=1, description="數量")
    price_per_item: int = Field(..., ge=0, description="單價（以分為單位）")
    message: Optional[str] = Field(None, description="項目備註")


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=1, description="數量")
    price_per_item: Optional[int] = Field(None, ge=0, description="單價（以分為單位）")
    message: Optional[str] = Field(None, description="項目備註")


class OrderDetailResponse(OrderDetailBase):
    order_detail_id: str
    order_id: str
    total_price: int = Field(..., description="小計（以分為單位）")
    product_name: Optional[str] = Field(None, description="商品名稱")
    product_type: Optional[str] = Field(None, description="商品類型")

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: str = Field(..., description="顧客 ID")
    appointment_id: Optional[str] = Field(None, description="預約 ID（可選）")
    notes: Optional[str] = Field(None, description="訂單備註")


class OrderCreate(OrderBase):
    coupon_code: Optional[str] = Field(None, description="優惠券代碼")
    details: List[OrderDetailCreate] = Field(..., description="訂單明細")


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, description="訂單狀態")
    notes: Optional[str] = Field(None, description="訂單備註")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['pending', 'confirmed', 'paid', 'processing', 'completed', 'cancelled', 'refunded']
            if v not in valid_statuses:
                raise ValueError(f'狀態必須是以下其中之一: {", ".join(valid_statuses)}')
        return v


class OrderResponse(OrderBase):
    order_id: str
    coupon_id: Optional[str] = Field(None, description="使用的優惠券 ID")
    coupon_code: Optional[str] = Field(None, description="使用的優惠券代碼")
    total_amount: int = Field(..., description="訂單總金額（以分為單位）")
    discount_amount: int = Field(..., description="折扣金額（以分為單位）")
    final_amount: int = Field(..., description="最終金額（以分為單位）")
    status: str = Field(..., description="訂單狀態")
    created_at: datetime
    updated_at: datetime
    details: List[OrderDetailResponse] = Field(default=[], description="訂單明細")

    class Config:
        from_attributes = True


class OrderSummary(BaseModel):
    order_id: str
    user_id: str
    appointment_id: Optional[str] = None
    total_amount: int
    discount_amount: int
    final_amount: int
    status: str
    created_at: datetime
    item_count: int = Field(..., description="商品項目數量")

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="訂單狀態")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'paid', 'processing', 'completed', 'cancelled', 'refunded']
        if v not in valid_statuses:
            raise ValueError(f'狀態必須是以下其中之一: {", ".join(valid_statuses)}')
        return v


class OrderFromAppointment(BaseModel):
    appointment_id: str = Field(..., description="預約 ID")
    coupon_code: Optional[str] = Field(None, description="優惠券代碼")
    notes: Optional[str] = Field(None, description="訂單備註")


class CouponApplication(BaseModel):
    coupon_code: str = Field(..., description="優惠券代碼")


class OrderCalculation(BaseModel):
    subtotal: int = Field(..., description="小計（以分為單位）")
    discount_amount: int = Field(..., description="折扣金額（以分為單位）")
    final_amount: int = Field(..., description="最終金額（以分為單位）")
    coupon_applied: Optional[str] = Field(None, description="已應用的優惠券代碼")
    
    
class OrderStatistics(BaseModel):
    total_orders: int = Field(..., description="總訂單數")
    total_revenue: int = Field(..., description="總營收（以分為單位）")
    pending_orders: int = Field(..., description="待處理訂單數")
    completed_orders: int = Field(..., description="已完成訂單數")
    cancelled_orders: int = Field(..., description="已取消訂單數")