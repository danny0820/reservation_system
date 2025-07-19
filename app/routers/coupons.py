from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user_models import User
from app.models.coupon_models import Coupon
from app.schemas.coupon_schemas import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponValidation,
    CouponValidationResult,
    CouponStatusUpdate,
    CouponStatistics,
    BulkCouponCreate
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.coupon_crud import coupon_crud

router = APIRouter()


# 管理員專用端點
@router.get(
    "/",
    response_model=List[CouponResponse],
    summary="獲取優惠券列表",
    description="(管理員權限) 獲取所有優惠券列表"
)
async def get_all_coupons(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    is_active: Optional[bool] = Query(None, description="是否啟用篩選"),
    discount_type: Optional[str] = Query(None, description="折扣類型篩選"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    coupons, total = coupon_crud.get_coupons(
        db, 
        skip=skip, 
        limit=limit,
        is_active=is_active,
        discount_type=discount_type
    )
    return coupons


@router.post(
    "/",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建新優惠券",
    description="(管理員權限) 創建新的優惠券"
)
async def create_coupon(
    coupon: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    # 檢查優惠券代碼是否已存在
    existing_coupon = coupon_crud.get_coupon_by_code(db, coupon.code)
    if existing_coupon:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="優惠券代碼已存在"
        )
    
    return coupon_crud.create_coupon(db, coupon)


@router.post(
    "/bulk",
    response_model=List[CouponResponse],
    status_code=status.HTTP_201_CREATED,
    summary="批量創建優惠券",
    description="(管理員權限) 批量創建多張優惠券"
)
async def bulk_create_coupons(
    bulk_coupon: BulkCouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    # 檢查是否會產生重複的優惠券代碼
    for i in range(1, bulk_coupon.count + 1):
        code = f"{bulk_coupon.base_code}{i:04d}"
        existing_coupon = coupon_crud.get_coupon_by_code(db, code)
        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"優惠券代碼 {code} 已存在"
            )
    
    return coupon_crud.bulk_create_coupons(db, bulk_coupon)


@router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="獲取優惠券詳情",
    description="根據優惠券 ID 獲取優惠券詳情"
)
async def get_coupon(
    coupon_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    coupon = coupon_crud.get_coupon_by_id(db, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    return coupon


@router.patch(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="更新優惠券",
    description="(管理員權限) 更新優惠券資訊"
)
async def update_coupon(
    coupon_id: str,
    coupon_update: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    coupon = coupon_crud.get_coupon_by_id(db, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    return coupon_crud.update_coupon(db, coupon, coupon_update)


@router.patch(
    "/{coupon_id}/status",
    response_model=CouponResponse,
    summary="更新優惠券狀態",
    description="(管理員權限) 更新優惠券啟用狀態"
)
async def update_coupon_status(
    coupon_id: str,
    status_update: CouponStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    coupon = coupon_crud.get_coupon_by_id(db, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    return coupon_crud.update_coupon_status(db, coupon, status_update.is_active)


@router.delete(
    "/{coupon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除優惠券",
    description="(管理員權限) 刪除優惠券"
)
async def delete_coupon(
    coupon_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    coupon = coupon_crud.get_coupon_by_id(db, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    # 檢查是否已被使用
    if coupon.used_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="已使用的優惠券無法刪除"
        )
    
    coupon_crud.delete_coupon(db, coupon)


# 用戶可用端點
@router.get(
    "/available",
    response_model=List[CouponResponse],
    summary="獲取可用優惠券",
    description="獲取用戶可用的優惠券列表"
)
async def get_available_coupons(
    order_amount: int = Query(..., ge=0, description="訂單金額（以分為單位）"),
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    coupons = coupon_crud.get_available_coupons(db, order_amount, skip, limit)
    return coupons


@router.post(
    "/validate",
    response_model=CouponValidationResult,
    summary="驗證優惠券",
    description="驗證優惠券是否可用並計算折扣"
)
async def validate_coupon(
    validation: CouponValidation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = coupon_crud.validate_coupon(db, validation.coupon_code, validation.order_amount)
    return result


@router.get(
    "/code/{coupon_code}",
    response_model=CouponResponse,
    summary="根據代碼獲取優惠券",
    description="根據優惠券代碼獲取優惠券詳情"
)
async def get_coupon_by_code(
    coupon_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    coupon = coupon_crud.get_coupon_by_code(db, coupon_code)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    # 非管理員只能查看啟用的優惠券
    if current_user.role != "admin" and not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="優惠券不存在"
        )
    
    return coupon


# 統計和管理端點
@router.get(
    "/statistics/overview",
    response_model=CouponStatistics,
    summary="獲取優惠券統計",
    description="(管理員權限) 獲取優惠券統計資料"
)
async def get_coupon_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    stats = coupon_crud.get_coupon_statistics(db)
    return CouponStatistics(**stats)


@router.get(
    "/expiring",
    response_model=List[CouponResponse],
    summary="獲取即將過期的優惠券",
    description="(管理員權限) 獲取即將過期的優惠券列表"
)
async def get_expiring_coupons(
    days_ahead: int = Query(7, ge=1, le=30, description="提前天數"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    coupons = coupon_crud.get_expiring_coupons(db, days_ahead)
    return coupons


@router.post(
    "/cleanup-expired",
    summary="清理過期優惠券",
    description="(管理員權限) 清理過期的優惠券（停用）"
)
async def cleanup_expired_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    count = coupon_crud.cleanup_expired_coupons(db)
    return {"message": f"已停用 {count} 張過期優惠券"}


# 特殊功能端點
@router.get(
    "/by-type/{discount_type}",
    response_model=List[CouponResponse],
    summary="根據折扣類型獲取優惠券",
    description="根據折扣類型獲取優惠券列表"
)
async def get_coupons_by_type(
    discount_type: str,
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    is_active: Optional[bool] = Query(True, description="是否只返回啟用的優惠券"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 驗證折扣類型
    if discount_type not in ["percentage", "fixed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無效的折扣類型，必須是 'percentage' 或 'fixed'"
        )
    
    # 非管理員只能查看啟用的優惠券
    if current_user.role != "admin":
        is_active = True
    
    coupons, total = coupon_crud.get_coupons(
        db, 
        skip=skip, 
        limit=limit,
        is_active=is_active,
        discount_type=discount_type
    )
    return coupons


@router.post(
    "/{coupon_id}/duplicate",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="複製優惠券",
    description="(管理員權限) 複製現有優惠券"
)
async def duplicate_coupon(
    coupon_id: str,
    new_code: str = Query(..., description="新優惠券代碼"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    original_coupon = coupon_crud.get_coupon_by_id(db, coupon_id)
    if not original_coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原優惠券不存在"
        )
    
    # 檢查新代碼是否已存在
    existing_coupon = coupon_crud.get_coupon_by_code(db, new_code)
    if existing_coupon:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="新優惠券代碼已存在"
        )
    
    # 創建新優惠券
    new_coupon_data = CouponCreate(
        code=new_code,
        name=f"{original_coupon.name} (複製)",
        description=original_coupon.description,
        discount_type=original_coupon.discount_type,
        discount_value=original_coupon.discount_value,
        min_order_amount=original_coupon.min_order_amount,
        max_discount_amount=original_coupon.max_discount_amount,
        usage_limit=original_coupon.usage_limit,
        is_active=True,  # 新優惠券預設啟用
        start_at=original_coupon.start_at,
        end_at=original_coupon.end_at
    )
    
    return coupon_crud.create_coupon(db, new_coupon_data)


# 驗證和測試端點
@router.post(
    "/test-validation",
    response_model=CouponValidationResult,
    summary="測試優惠券驗證",
    description="(管理員權限) 測試優惠券驗證邏輯"
)
async def test_coupon_validation(
    validation: CouponValidation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """
    測試優惠券驗證邏輯，管理員可以測試任何優惠券的驗證結果
    """
    result = coupon_crud.validate_coupon(db, validation.coupon_code, validation.order_amount)
    return result