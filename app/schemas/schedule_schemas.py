from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time
import enum


class TimeOffStatus(str, enum.Enum):
    """請假狀態枚舉"""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class StylistSchedulesBase(BaseModel):
    stylist_id: str = Field(..., description="設計師 ID")
    day_of_week: int = Field(
        ..., ge=0, le=6, description="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    )
    start_time: time = Field(..., description="開始工作時間")
    end_time: time = Field(..., description="結束工作時間")

    @validator("end_time")
    def validate_end_time(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("結束時間必須晚於開始時間")
        return v


class StylistSchedulesCreate(StylistSchedulesBase):
    pass


class StylistSchedulesUpdate(BaseModel):
    start_time: Optional[time] = Field(None, description="開始工作時間")
    end_time: Optional[time] = Field(None, description="結束工作時間")

    @validator("end_time")
    def validate_end_time(cls, v, values):
        if "start_time" in values and values["start_time"] and v:
            if v <= values["start_time"]:
                raise ValueError("結束時間必須晚於開始時間")
        return v


class StylistSchedulesResponse(StylistSchedulesBase):
    schedule_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StylistTimeOffBase(BaseModel):
    stylist_id: str = Field(..., description="設計師 ID")
    start_datetime: datetime = Field(..., description="請假開始時間")
    end_datetime: datetime = Field(..., description="請假結束時間")
    reason: Optional[str] = Field(None, description="請假原因")

    @validator("end_datetime")
    def validate_end_datetime(cls, v, values):
        if "start_datetime" in values and v <= values["start_datetime"]:
            raise ValueError("結束時間必須晚於開始時間")
        return v

    @validator("start_datetime")
    def validate_start_datetime(cls, v):
        if v < datetime.now():
            raise ValueError("開始時間不能早於當前時間")
        return v


class StylistTimeOffCreate(StylistTimeOffBase):
    pass


class StylistTimeOffUpdate(BaseModel):
    start_datetime: Optional[datetime] = Field(None, description="請假開始時間")
    end_datetime: Optional[datetime] = Field(None, description="請假結束時間")
    reason: Optional[str] = Field(None, description="請假原因")
    status: Optional[TimeOffStatus] = Field(None, description="請假狀態")

    @validator("end_datetime")
    def validate_end_datetime(cls, v, values):
        if "start_datetime" in values and values["start_datetime"] and v:
            if v <= values["start_datetime"]:
                raise ValueError("結束時間必須晚於開始時間")
        return v


class StylistTimeOffResponse(StylistTimeOffBase):
    time_off_id: str
    status: TimeOffStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StylistTimeOffStatusUpdate(BaseModel):
    """請假狀態更新專用模型"""

    status: TimeOffStatus = Field(..., description="請假狀態")


class WeeklyStylistScheduleResponse(BaseModel):
    """設計師一週排班回應格式"""

    stylist_id: str
    stylist_name: str
    schedules: dict = Field(
        ..., description="一週排班，key為星期幾(0-6)，value為排班詳情"
    )


class StylistAvailabilityResponse(BaseModel):
    """設計師可用時間回應格式"""

    stylist_id: str
    stylist_name: str
    date: datetime
    available_slots: List[dict] = Field(..., description="可用時間段列表")
    total_available_hours: float = Field(..., description="總可用時數")


class ScheduleConflictResponse(BaseModel):
    """排班衝突檢查回應格式"""

    has_conflict: bool = Field(..., description="是否有衝突")
    conflict_details: List[dict] = Field(default=[], description="衝突詳情列表")
    suggestions: List[str] = Field(default=[], description="建議解決方案")
