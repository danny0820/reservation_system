from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="商品/服務名稱")
    description: Optional[str] = Field(None, description="詳細描述")
    price: int = Field(..., ge=0, description="價格（以分為單位）")
    duration_time: Optional[int] = Field(None, ge=0, description="服務耗時（分鐘）")
    stock_quantity: int = Field(default=0, ge=0, description="庫存數量")
    is_active: bool = Field(default=True, description="是否啟用")
    is_service: bool = Field(default=False, description="是否為服務項目")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=150, description="商品/服務名稱"
    )
    description: Optional[str] = Field(None, description="詳細描述")
    price: Optional[int] = Field(None, ge=0, description="價格（以分為單位）")
    duration_time: Optional[int] = Field(None, ge=0, description="服務耗時（分鐘）")
    stock_quantity: Optional[int] = Field(None, ge=0, description="庫存數量")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    is_service: Optional[bool] = Field(None, description="是否為服務項目")


class ProductResponse(ProductBase):
    product_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="啟用狀態")


class ProductStockUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0, description="庫存數量")


class ProductPriceUpdate(BaseModel):
    price: int = Field(..., ge=0, description="價格（以分為單位）")
