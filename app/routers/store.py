from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.user_models import User
from app.models.store_models import StoreBusinessHours, StoreClosures
from app.schemas.store_schemas import (
    StoreBusinessHoursCreate,
    StoreBusinessHoursUpdate,
    StoreBusinessHoursResponse,
    StoreClosuresCreate,
    StoreClosuresUpdate,
    StoreClosuresResponse,
    WeeklyBusinessHoursResponse,
    StoreStatusResponse,
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.store_crud import store_crud

router = APIRouter()

# === 營業時間管理 ===


@router.get(
    "/business-hours",
    response_model=WeeklyBusinessHoursResponse,
    summary="獲取營業時間",
    description="獲取店面一週的營業時間設定",
)
async def get_business_hours(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    weekly_hours = store_crud.get_weekly_business_hours(db)
    return weekly_hours


@router.post(
    "/business-hours",
    response_model=StoreBusinessHoursResponse,
    status_code=status.HTTP_201_CREATED,
    summary="設定營業時間",
    description="(管理員權限) 設定或更新指定日期的營業時間",
)
async def create_or_update_business_hours(
    hours_data: StoreBusinessHoursCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return store_crud.create_or_update_business_hours(
        db, hours_data.day_of_week, hours_data
    )


@router.patch(
    "/business-hours/{day_of_week}",
    response_model=StoreBusinessHoursResponse,
    summary="更新特定日期營業時間",
    description="(管理員權限) 更新指定星期幾的營業時間",
)
async def update_business_hours_by_day(
    day_of_week: int = Path(
        ..., ge=0, le=6, description="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    ),
    hours_update: StoreBusinessHoursUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    hours = store_crud.update_business_hours(db, day_of_week, hours_update)
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business hours for day {day_of_week} not found",
        )
    return hours


@router.get(
    "/business-hours/{day_of_week}",
    response_model=StoreBusinessHoursResponse,
    summary="獲取特定日期營業時間",
    description="獲取指定星期幾的營業時間",
)
async def get_business_hours_by_day(
    day_of_week: int = Path(
        ..., ge=0, le=6, description="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    hours = store_crud.get_business_hours_by_day(db, day_of_week)
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business hours for day {day_of_week} not found",
        )
    return hours


# === 臨時休業管理 ===


@router.get(
    "/closures",
    response_model=List[StoreClosuresResponse],
    summary="獲取休業記錄",
    description="獲取店面的臨時休業記錄列表",
)
async def get_store_closures(
    start_date: Optional[date] = Query(None, description="查詢開始日期"),
    end_date: Optional[date] = Query(None, description="查詢結束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    closures = store_crud.get_closures(db, start_date=start_date, end_date=end_date)
    return closures


@router.post(
    "/closures",
    response_model=StoreClosuresResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增休業日期",
    description="(管理員權限) 新增店面臨時休業日期",
)
async def create_store_closure(
    closure_data: StoreClosuresCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return store_crud.create_closure(db, closure_data)


@router.get(
    "/closures/{closure_id}",
    response_model=StoreClosuresResponse,
    summary="獲取特定休業記錄",
    description="根據休業ID獲取特定的休業記錄",
)
async def get_store_closure_by_id(
    closure_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    closure = store_crud.get_closure_by_id(db, closure_id)
    if not closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store closure not found"
        )
    return closure


@router.patch(
    "/closures/{closure_id}",
    response_model=StoreClosuresResponse,
    summary="更新休業記錄",
    description="(管理員權限) 更新指定的休業記錄",
)
async def update_store_closure(
    closure_id: str,
    closure_update: StoreClosuresUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    closure = store_crud.get_closure_by_id(db, closure_id)
    if not closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store closure not found"
        )

    return store_crud.update_closure(db, closure, closure_update)


@router.delete(
    "/closures/{closure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="取消休業",
    description="(管理員權限) 取消指定的休業記錄",
)
async def delete_store_closure(
    closure_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    closure = store_crud.get_closure_by_id(db, closure_id)
    if not closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Store closure not found"
        )

    store_crud.delete_closure(db, closure)


# === 營業狀態查詢 ===


@router.get(
    "/status",
    response_model=StoreStatusResponse,
    summary="獲取店面狀態",
    description="獲取店面當前營業狀態和相關資訊",
)
async def get_store_status(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    current_time = datetime.now()
    is_open = store_crud.is_store_open(db)
    next_open_time = None
    next_close_time = None

    if not is_open:
        next_open_time = store_crud.get_next_open_time(db)
    else:
        # 如果目前營業中，計算何時關店
        day_of_week = current_time.weekday()
        adjusted_day = 0 if day_of_week == 6 else day_of_week + 1

        business_hours = store_crud.get_business_hours_by_day(db, adjusted_day)
        if business_hours and business_hours.close_time:
            next_close_time = datetime.combine(
                current_time.date(), business_hours.close_time
            )

    return StoreStatusResponse(
        is_open=is_open,
        current_time=current_time,
        next_open_time=next_open_time,
        next_close_time=next_close_time,
    )


@router.get(
    "/is-open",
    response_model=dict,
    summary="檢查是否營業中",
    description="快速檢查店面是否正在營業",
)
async def check_store_is_open(
    check_time: Optional[datetime] = Query(
        None, description="檢查的時間點（預設為當前時間）"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    is_open = store_crud.is_store_open(db, check_time)
    check_datetime = check_time or datetime.now()

    return {
        "is_open": is_open,
        "check_time": check_datetime,
        "message": "店面營業中" if is_open else "店面休息中",
    }


@router.get(
    "/next-open",
    response_model=dict,
    summary="獲取下次營業時間",
    description="獲取店面下次開始營業的時間",
)
async def get_next_open_time(
    from_time: Optional[datetime] = Query(
        None, description="從什麼時間開始查找（預設為當前時間）"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    next_open = store_crud.get_next_open_time(db, from_time)
    from_datetime = from_time or datetime.now()

    return {
        "next_open_time": next_open,
        "from_time": from_datetime,
        "message": "已找到下次營業時間" if next_open else "未來一週內無營業時間",
    }
