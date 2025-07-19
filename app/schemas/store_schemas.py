from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, time


class StoreBusinessHoursBase(BaseModel):
    day_of_week: int = Field(
        ..., ge=0, le=6, description="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    )
    open_time: Optional[time] = Field(None, description="開始營業時間")
    close_time: Optional[time] = Field(None, description="結束營業時間")
    is_closed: bool = Field(default=False, description="當天是否固定公休")

    @validator("close_time")
    def validate_close_time(cls, v, values):
        if "open_time" in values and values["open_time"] and v:
            if v <= values["open_time"]:
                raise ValueError("結束營業時間必須晚於開始營業時間")
        return v

    @validator("is_closed")
    def validate_closed_day(cls, v, values):
        # 如果設定為公休日，自動清空營業時間
        if v:
            values["open_time"] = None
            values["close_time"] = None
        return v



class StoreBusinessHoursCreate(StoreBusinessHoursBase):
    @validator("open_time")
    def validate_open_time_required(cls, v, values):
        # 如果不是公休日，則營業時間為必填
        if not values.get("is_closed", False) and v is None:
            raise ValueError("非公休日必須設定開始營業時間")
        return v


class StoreBusinessHoursUpdate(BaseModel):
    open_time: Optional[time] = Field(None, description="開始營業時間")
    close_time: Optional[time] = Field(None, description="結束營業時間")
    is_closed: Optional[bool] = Field(None, description="當天是否固定公休")

    @validator("close_time")
    def validate_close_time(cls, v, values):
        if "open_time" in values and values["open_time"] and v:
            if v <= values["open_time"]:
                raise ValueError("結束營業時間必須晚於開始營業時間")
        return v

    @validator("is_closed")
    def validate_closed_day_update(cls, v, values):
        # 如果設定為公休日，自動清空營業時間
        if v:
            values["open_time"] = None
            values["close_time"] = None
        return v


class StoreBusinessHoursResponse(StoreBusinessHoursBase):
    hour_id: str

    class Config:
        from_attributes = True


class StoreClosuresBase(BaseModel):
    start_datetime: datetime = Field(..., description="休業開始時間")
    end_datetime: datetime = Field(..., description="休業結束時間")
    reason: Optional[str] = Field(None, description="休業原因")

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


class StoreClosuresCreate(StoreClosuresBase):
    pass


class StoreClosuresUpdate(BaseModel):
    start_datetime: Optional[datetime] = Field(None, description="休業開始時間")
    end_datetime: Optional[datetime] = Field(None, description="休業結束時間")
    reason: Optional[str] = Field(None, description="休業原因")

    @validator("end_datetime")
    def validate_end_datetime(cls, v, values):
        if "start_datetime" in values and values["start_datetime"] and v:
            if v <= values["start_datetime"]:
                raise ValueError("結束時間必須晚於開始時間")
        return v


class StoreClosuresResponse(StoreClosuresBase):
    closure_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyBusinessHoursResponse(BaseModel):
    """一週營業時間回應格式"""

    monday: Optional[StoreBusinessHoursResponse]
    tuesday: Optional[StoreBusinessHoursResponse]
    wednesday: Optional[StoreBusinessHoursResponse]
    thursday: Optional[StoreBusinessHoursResponse]
    friday: Optional[StoreBusinessHoursResponse]
    saturday: Optional[StoreBusinessHoursResponse]
    sunday: Optional[StoreBusinessHoursResponse]


class StoreStatusResponse(BaseModel):
    """店面狀態回應格式"""

    is_open: bool = Field(..., description="目前是否營業中")
    current_time: datetime = Field(..., description="當前時間")
    next_open_time: Optional[datetime] = Field(None, description="下次營業時間")
    next_close_time: Optional[datetime] = Field(None, description="下次關店時間")
