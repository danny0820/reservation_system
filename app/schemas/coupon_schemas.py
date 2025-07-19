from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CouponBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, description="優惠券代碼")
    name: str = Field(..., min_length=1, max_length=255, description="優惠券名稱")
    description: Optional[str] = Field(None, description="優惠券描述")
    discount_type: str = Field(..., description="折扣類型 (percentage/fixed)")
    discount_value: int = Field(..., ge=0, description="折扣值")
    min_order_amount: Optional[int] = Field(None, ge=0, description="最低消費金額（以分為單位）")
    max_discount_amount: Optional[int] = Field(None, ge=0, description="最大折扣金額（以分為單位）")
    usage_limit: Optional[int] = Field(None, ge=1, description="使用次數限制")
    is_active: bool = Field(default=True, description="是否啟用")
    start_at: Optional[datetime] = Field(None, description="優惠券開始時間")
    end_at: Optional[datetime] = Field(None, description="優惠券結束時間")

    @validator('discount_type')
    def validate_discount_type(cls, v):
        valid_types = ['percentage', 'fixed']
        if v not in valid_types:
            raise ValueError(f'折扣類型必須是以下其中之一: {", ".join(valid_types)}')
        return v

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if 'discount_type' in values:
            if values['discount_type'] == 'percentage' and v > 10000:  # 100.00%
                raise ValueError('百分比折扣不能超過 100%')
            elif values['discount_type'] == 'fixed' and v <= 0:
                raise ValueError('固定金額折扣必須大於 0')
        return v

    @validator('end_at')
    def validate_end_at(cls, v, values):
        if v and 'start_at' in values and values['start_at'] and v <= values['start_at']:
            raise ValueError('結束時間必須晚於開始時間')
        return v

    @validator('max_discount_amount')
    def validate_max_discount_amount(cls, v, values):
        if v and 'discount_type' in values and values['discount_type'] == 'percentage':
            if 'discount_value' in values and v <= 0:
                raise ValueError('百分比折扣的最大折扣金額必須大於 0')
        return v


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="優惠券名稱")
    description: Optional[str] = Field(None, description="優惠券描述")
    discount_type: Optional[str] = Field(None, description="折扣類型 (percentage/fixed)")
    discount_value: Optional[int] = Field(None, ge=0, description="折扣值")
    min_order_amount: Optional[int] = Field(None, ge=0, description="最低消費金額（以分為單位）")
    max_discount_amount: Optional[int] = Field(None, ge=0, description="最大折扣金額（以分為單位）")
    usage_limit: Optional[int] = Field(None, ge=1, description="使用次數限制")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    start_at: Optional[datetime] = Field(None, description="優惠券開始時間")
    end_at: Optional[datetime] = Field(None, description="優惠券結束時間")

    @validator('discount_type')
    def validate_discount_type(cls, v):
        if v is not None:
            valid_types = ['percentage', 'fixed']
            if v not in valid_types:
                raise ValueError(f'折扣類型必須是以下其中之一: {", ".join(valid_types)}')
        return v

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if v is not None and 'discount_type' in values and values['discount_type']:
            if values['discount_type'] == 'percentage' and v > 10000:  # 100.00%
                raise ValueError('百分比折扣不能超過 100%')
            elif values['discount_type'] == 'fixed' and v <= 0:
                raise ValueError('固定金額折扣必須大於 0')
        return v


class CouponResponse(CouponBase):
    coupon_id: str
    used_count: int = Field(..., description="已使用次數")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CouponValidation(BaseModel):
    coupon_code: str = Field(..., description="優惠券代碼")
    order_amount: int = Field(..., ge=0, description="訂單金額（以分為單位）")


class CouponValidationResult(BaseModel):
    is_valid: bool = Field(..., description="是否有效")
    coupon_id: Optional[str] = Field(None, description="優惠券 ID")
    coupon_name: Optional[str] = Field(None, description="優惠券名稱")
    discount_amount: int = Field(default=0, description="折扣金額（以分為單位）")
    final_amount: int = Field(..., description="折扣後金額（以分為單位）")
    error_message: Optional[str] = Field(None, description="錯誤訊息")


class CouponUsage(BaseModel):
    coupon_id: str
    coupon_code: str
    coupon_name: str
    order_id: str
    user_id: str
    discount_amount: int
    used_at: datetime

    class Config:
        from_attributes = True


class CouponStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="是否啟用")


class CouponStatistics(BaseModel):
    total_coupons: int = Field(..., description="總優惠券數")
    active_coupons: int = Field(..., description="啟用的優惠券數")
    used_coupons: int = Field(..., description="已使用的優惠券數")
    total_discount_amount: int = Field(..., description="總折扣金額（以分為單位）")
    most_used_coupon: Optional[str] = Field(None, description="最常使用的優惠券")


class BulkCouponCreate(BaseModel):
    base_code: str = Field(..., min_length=3, max_length=30, description="優惠券代碼前綴")
    name_template: str = Field(..., description="優惠券名稱模板 (使用 {index} 作為佔位符)")
    count: int = Field(..., ge=1, le=1000, description="生成數量")
    discount_type: str = Field(..., description="折扣類型 (percentage/fixed)")
    discount_value: int = Field(..., ge=0, description="折扣值")
    min_order_amount: Optional[int] = Field(None, ge=0, description="最低消費金額（以分為單位）")
    max_discount_amount: Optional[int] = Field(None, ge=0, description="最大折扣金額（以分為單位）")
    usage_limit: Optional[int] = Field(None, ge=1, description="使用次數限制")
    start_at: Optional[datetime] = Field(None, description="優惠券開始時間")
    end_at: Optional[datetime] = Field(None, description="優惠券結束時間")

    @validator('discount_type')
    def validate_discount_type(cls, v):
        valid_types = ['percentage', 'fixed']
        if v not in valid_types:
            raise ValueError(f'折扣類型必須是以下其中之一: {", ".join(valid_types)}')
        return v