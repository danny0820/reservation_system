from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AppointmentBase(BaseModel):
    user_id: str = Field(..., description="預約顧客的 ID")
    stylist_id: str = Field(..., description="負責服務的設計師 ID")
    start_time: datetime = Field(..., description="預約開始時間")
    end_time: datetime = Field(..., description="預約結束時間")
    status: str = Field(..., description="預約狀態")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('結束時間必須晚於開始時間')
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = Field(None, description="預約開始時間")
    end_time: Optional[datetime] = Field(None, description="預約結束時間")
    status: Optional[str] = Field(None, description="預約狀態")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('結束時間必須晚於開始時間')
        return v


class AppointmentResponse(AppointmentBase):
    appointment_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AppointmentServices 相關的 Schemas
class AppointmentServiceBase(BaseModel):
    appointment_id: str = Field(..., description="預約 ID")
    product_id: str = Field(..., description="服務項目 ID")


class AppointmentServiceCreate(BaseModel):
    product_id: str = Field(..., description="服務項目 ID")


class AppointmentServiceResponse(AppointmentServiceBase):
    product_name: Optional[str] = Field(None, description="服務項目名稱")
    product_price: Optional[int] = Field(None, description="服務價格（以分為單位）")
    duration_time: Optional[int] = Field(None, description="服務耗時（分鐘）")

    class Config:
        from_attributes = True


class AppointmentServiceBulkCreate(BaseModel):
    product_ids: List[str] = Field(..., description="服務項目 ID 列表")


class AppointmentCalculation(BaseModel):
    appointment_id: str = Field(..., description="預約 ID")
    total_services: int = Field(..., description="服務項目總數")
    total_duration: int = Field(..., description="總耗時（分鐘）")
    total_price: int = Field(..., description="總價格（以分為單位）")
    services: List[AppointmentServiceResponse] = Field(..., description="服務項目列表")


class AppointmentWithServicesResponse(AppointmentResponse):
    services: List[AppointmentServiceResponse] = Field(default=[], description="預約的服務項目")
    total_duration: Optional[int] = Field(None, description="預約總耗時（分鐘）")
    total_price: Optional[int] = Field(None, description="預約總價格（以分為單位）")


class AppointmentStatusUpdate(BaseModel):
    status: str = Field(..., description="預約狀態")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']
        if v not in valid_statuses:
            raise ValueError(f'狀態必須是以下其中之一: {", ".join(valid_statuses)}')
        return v