from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.user_models import User
from app.models.schedule_models import StylistSchedules, StylistTimeOff
from app.schemas.schedule_schemas import (
    StylistSchedulesCreate,
    StylistSchedulesUpdate,
    StylistSchedulesResponse,
    StylistTimeOffCreate,
    StylistTimeOffUpdate,
    StylistTimeOffResponse,
    StylistTimeOffStatusUpdate,
    TimeOffStatus,
    WeeklyStylistScheduleResponse,
    StylistAvailabilityResponse,
    ScheduleConflictResponse,
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.schedule_crud import schedule_crud
from app.crud.user_crud import user_crud

router = APIRouter()

# === 設計師排班管理 ===


@router.get(
    "/stylists/{stylist_id}",
    response_model=List[StylistSchedulesResponse],
    summary="獲取設計師排班",
    description="獲取指定設計師的所有排班記錄",
)
async def get_stylist_schedules(
    stylist_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 設計師只能查看自己的排班，管理員可以查看所有
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    schedules = schedule_crud.get_stylist_all_schedules(db, stylist_id)
    return schedules


@router.post(
    "/stylists/{stylist_id}",
    response_model=StylistSchedulesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="設定設計師排班",
    description="為指定設計師設定新的排班時間",
)
async def create_stylist_schedule(
    stylist_id: str,
    schedule_data: StylistSchedulesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 只有管理員或設計師本人可以設定排班
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # 確保 stylist_id 匹配
    schedule_data.stylist_id = stylist_id

    # 檢查衝突
    conflict_result = schedule_crud.check_schedule_conflicts(
        db,
        stylist_id,
        schedule_data.day_of_week,
        schedule_data.start_time,
        schedule_data.end_time,
    )

    if conflict_result["has_conflict"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Schedule conflict detected",
                "conflicts": conflict_result["conflict_details"],
                "suggestions": conflict_result["suggestions"],
            },
        )

    return schedule_crud.create_or_update_schedule(db, schedule_data)


@router.patch(
    "/stylists/{stylist_id}/schedules/{schedule_id}",
    response_model=StylistSchedulesResponse,
    summary="更新設計師排班",
    description="更新指定設計師的排班時間",
)
async def update_stylist_schedule(
    stylist_id: str,
    schedule_id: str,
    schedule_update: StylistSchedulesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 檢查排班是否存在
    schedule = schedule_crud.get_schedule_by_id(db, schedule_id)
    if not schedule or schedule.stylist_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )

    # 只有管理員或設計師本人可以更新排班
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return schedule_crud.update_schedule(db, schedule, schedule_update)


@router.delete(
    "/stylists/{stylist_id}/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除設計師排班",
    description="刪除指定設計師的排班記錄",
)
async def delete_stylist_schedule(
    stylist_id: str,
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 檢查排班是否存在
    schedule = schedule_crud.get_schedule_by_id(db, schedule_id)
    if not schedule or schedule.stylist_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )

    # 只有管理員或設計師本人可以刪除排班
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    schedule_crud.delete_schedule(db, schedule)


@router.get(
    "/stylists/{stylist_id}/available",
    response_model=StylistAvailabilityResponse,
    summary="查看設計師可預約時間",
    description="查看指定設計師在特定日期的可預約時間段",
)
async def get_stylist_availability(
    stylist_id: str,
    target_date: date = Query(..., description="目標日期"),
    slot_duration: int = Query(60, ge=15, le=480, description="時間段長度（分鐘）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    available_slots = schedule_crud.get_stylist_available_slots(
        db, stylist_id, target_date, slot_duration
    )

    total_hours = len(available_slots) * slot_duration / 60

    return StylistAvailabilityResponse(
        stylist_id=stylist_id,
        stylist_name=f"{stylist.first_name} {stylist.last_name}".strip()
        or stylist.username,
        date=datetime.combine(target_date, datetime.min.time()),
        available_slots=available_slots,
        total_available_hours=total_hours,
    )


# === 設計師請假管理 ===


@router.post(
    "/stylists/{stylist_id}/time-off",
    response_model=StylistTimeOffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="申請請假",
    description="設計師申請請假或管理員為設計師安排請假",
)
async def create_stylist_time_off(
    stylist_id: str,
    time_off_data: StylistTimeOffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 只有管理員或設計師本人可以申請請假
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # 確保 stylist_id 匹配
    time_off_data.stylist_id = stylist_id

    return schedule_crud.create_time_off(db, time_off_data)


@router.get(
    "/time-off",
    response_model=List[StylistTimeOffResponse],
    summary="查看請假記錄",
    description="查看所有設計師的請假記錄（管理員）或自己的請假記錄（設計師）",
)
async def get_time_off_records(
    stylist_id: Optional[str] = Query(None, description="設計師ID篩選"),
    start_date: Optional[date] = Query(None, description="查詢開始日期"),
    end_date: Optional[date] = Query(None, description="查詢結束日期"),
    time_off_status: Optional[TimeOffStatus] = Query(None, description="請假狀態篩選"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 如果不是管理員，只能查看自己的請假記錄
    if current_user.role not in ["admin"]:
        if stylist_id and stylist_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        stylist_id = current_user.user_id

    if stylist_id:
        # 檢查設計師是否存在
        stylist = user_crud.get_user_by_id(db, stylist_id)
        if not stylist or stylist.role != "stylist":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
            )

        time_offs = schedule_crud.get_stylist_time_offs(
            db, stylist_id, start_date=start_date, end_date=end_date, status=time_off_status
        )
    else:
        # 管理員查看所有請假記錄
        time_offs = schedule_crud.get_all_time_offs(
            db, start_date=start_date, end_date=end_date, status=time_off_status
        )

    return time_offs


@router.patch(
    "/time-off/{time_off_id}",
    response_model=StylistTimeOffResponse,
    summary="更新請假記錄",
    description="更新請假記錄的詳細資訊",
)
async def update_time_off_record(
    time_off_id: str,
    time_off_update: StylistTimeOffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    time_off = schedule_crud.get_time_off_by_id(db, time_off_id)
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Time off record not found"
        )

    # 只有管理員或申請人本人可以更新
    if (
        current_user.role not in ["admin"]
        and current_user.user_id != time_off.stylist_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # 非管理員不能修改狀態
    if current_user.role not in ["admin"] and time_off_update.status is not None:
        time_off_update.status = None

    return schedule_crud.update_time_off(db, time_off, time_off_update)


@router.patch(
    "/time-off/{time_off_id}/status",
    response_model=StylistTimeOffResponse,
    summary="更新請假狀態",
    description="(管理員權限) 批准或拒絕請假申請",
)
async def update_time_off_status(
    time_off_id: str,
    status_update: StylistTimeOffStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    time_off = schedule_crud.get_time_off_by_id(db, time_off_id)
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Time off record not found"
        )

    return schedule_crud.update_time_off_status(db, time_off, status_update.status)


@router.delete(
    "/time-off/{time_off_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除請假記錄",
    description="刪除請假記錄",
)
async def delete_time_off_record(
    time_off_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    time_off = schedule_crud.get_time_off_by_id(db, time_off_id)
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Time off record not found"
        )

    # 只有管理員或申請人本人可以刪除
    if (
        current_user.role not in ["admin"]
        and current_user.user_id != time_off.stylist_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    schedule_crud.delete_time_off(db, time_off)


# === 整體排班查詢 ===


@router.get(
    "/",
    response_model=List[StylistSchedulesResponse],
    summary="獲取所有設計師排班",
    description="(管理員權限) 獲取所有設計師的排班記錄",
)
async def get_all_schedules(
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="篩選特定星期幾"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    schedules = schedule_crud.get_all_stylists_schedules(db, day_of_week=day_of_week)
    return schedules


@router.get(
    "/check-conflict",
    response_model=ScheduleConflictResponse,
    summary="檢查排班衝突",
    description="檢查新排班是否與現有安排衝突",
)
async def check_schedule_conflict(
    stylist_id: str = Query(..., description="設計師ID"),
    day_of_week: int = Query(..., ge=0, le=6, description="星期幾"),
    start_time: str = Query(..., description="開始時間 (HH:MM)"),
    end_time: str = Query(..., description="結束時間 (HH:MM)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查設計師是否存在
    stylist = user_crud.get_user_by_id(db, stylist_id)
    if not stylist or stylist.role != "stylist":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found"
        )

    # 只有管理員或設計師本人可以檢查衝突
    if current_user.role not in ["admin"] and current_user.user_id != stylist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        from datetime import time as datetime_time

        start_time_obj = datetime_time.fromisoformat(start_time)
        end_time_obj = datetime_time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Please use HH:MM format.",
        )

    conflict_result = schedule_crud.check_schedule_conflicts(
        db, stylist_id, day_of_week, start_time_obj, end_time_obj
    )

    return ScheduleConflictResponse(**conflict_result)
