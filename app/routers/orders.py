from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user_models import User
from app.models.order_models import Order, OrderDetail
from app.schemas.order_schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderSummary,
    OrderStatusUpdate,
    OrderFromAppointment,
    OrderDetailCreate,
    OrderDetailUpdate,
    OrderDetailResponse,
    CouponApplication,
    OrderCalculation,
    OrderStatistics
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.order_crud import order_crud, order_detail_crud

router = APIRouter()


# 訂單管理端點
@router.get(
    "/",
    response_model=List[OrderSummary],
    summary="獲取訂單列表",
    description="獲取訂單列表，支援分頁和篩選"
)
async def get_orders(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    user_id: Optional[str] = Query(None, description="客戶 ID 篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    start_date: Optional[datetime] = Query(None, description="開始日期篩選"),
    end_date: Optional[datetime] = Query(None, description="結束日期篩選"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 非管理員只能查看自己的訂單
    if current_user.role != "admin":
        user_id = current_user.user_id

    orders, total = order_crud.get_orders(
        db, 
        skip=skip, 
        limit=limit,
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    # 轉換為摘要格式
    return [
        OrderSummary(
            order_id=order.order_id,
            user_id=order.user_id,
            appointment_id=order.appointment_id,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            status=order.status,
            created_at=order.created_at,
            item_count=len(order.details)
        ) for order in orders
    ]


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建新訂單",
    description="創建新的訂單"
)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查是否為客戶本人或管理員
    if current_user.role == "customer" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="客戶只能為自己創建訂單"
        )
    
    try:
        created_order = order_crud.create_order(db, order)
        return created_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/from-appointment",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="從預約創建訂單",
    description="從現有預約創建訂單"
)
async def create_order_from_appointment(
    order_data: OrderFromAppointment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        created_order = order_crud.create_order_from_appointment(
            db, 
            order_data.appointment_id, 
            current_user.user_id,
            order_data.coupon_code,
            order_data.notes
        )
        return created_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="獲取訂單詳情",
    description="根據訂單 ID 獲取訂單詳情"
)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看此訂單"
        )
    
    return order


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="更新訂單",
    description="更新訂單資訊"
)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限 - 只有管理員或訂單所有者可以更新
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改此訂單"
        )
    
    return order_crud.update_order(db, order, order_update)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="更新訂單狀態",
    description="更新訂單狀態"
)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 狀態更新權限檢查
    if current_user.role == "customer":
        # 客戶只能取消自己的訂單
        if status_update.status != "cancelled" or order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="客戶只能取消自己的訂單"
            )
    elif current_user.role == "stylist":
        # 設計師可以更新相關預約的訂單狀態
        if order.appointment_id:
            from app.crud.appointment_crud import appointment_crud
            appointment = appointment_crud.get_appointment_by_id(db, order.appointment_id)
            if not appointment or appointment.stylist_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="設計師只能更新自己預約相關的訂單"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此訂單狀態"
            )
    
    return order_crud.update_order_status(db, order, status_update.status)


@router.post(
    "/{order_id}/apply-coupon",
    response_model=OrderResponse,
    summary="應用優惠券",
    description="為訂單應用優惠券"
)
async def apply_coupon_to_order(
    order_id: str,
    coupon_application: CouponApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改此訂單"
        )
    
    # 檢查訂單狀態
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能為待處理或已確認的訂單應用優惠券"
        )
    
    try:
        updated_order = order_crud.apply_coupon_to_order(db, order, coupon_application.coupon_code)
        return updated_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{order_id}/coupon",
    response_model=OrderResponse,
    summary="移除優惠券",
    description="從訂單中移除優惠券"
)
async def remove_coupon_from_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改此訂單"
        )
    
    # 檢查訂單狀態
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能為待處理或已確認的訂單移除優惠券"
        )
    
    return order_crud.remove_coupon_from_order(db, order)


@router.get(
    "/{order_id}/calculation",
    response_model=OrderCalculation,
    summary="獲取訂單計算",
    description="計算訂單的金額詳情"
)
async def get_order_calculation(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看此訂單計算"
        )
    
    try:
        calculation = order_crud.calculate_order_amount(db, order_id)
        return calculation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除訂單",
    description="刪除訂單"
)
async def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),  # 只有管理員可以刪除
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    order_crud.delete_order(db, order)


# 訂單明細管理端點
@router.get(
    "/{order_id}/details",
    response_model=List[OrderDetailResponse],
    summary="獲取訂單明細",
    description="獲取訂單的所有明細項目"
)
async def get_order_details(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看此訂單明細"
        )
    
    details = order_detail_crud.get_order_details(db, order_id)
    return [
        OrderDetailResponse(
            order_detail_id=detail.order_detail_id,
            order_id=detail.order_id,
            product_id=detail.product_id,
            quantity=detail.quantity,
            price_per_item=detail.price_per_item,
            total_price=detail.total_price,
            message=detail.message,
            product_name=detail.product.name if detail.product else None,
            product_type="service" if detail.product and detail.product.is_service else "product"
        ) for detail in details
    ]


@router.post(
    "/{order_id}/details",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增訂單明細",
    description="為訂單新增明細項目"
)
async def add_detail_to_order(
    order_id: str,
    detail: OrderDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改此訂單"
        )
    
    # 檢查訂單狀態
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能為待處理或已確認的訂單新增項目"
        )
    
    created_detail = order_detail_crud.add_detail_to_order(db, order_id, detail)
    
    return OrderDetailResponse(
        order_detail_id=created_detail.order_detail_id,
        order_id=created_detail.order_id,
        product_id=created_detail.product_id,
        quantity=created_detail.quantity,
        price_per_item=created_detail.price_per_item,
        total_price=created_detail.total_price,
        message=created_detail.message,
        product_name=created_detail.product.name if created_detail.product else None,
        product_type="service" if created_detail.product and created_detail.product.is_service else "product"
    )


@router.patch(
    "/{order_id}/details/{detail_id}",
    response_model=OrderDetailResponse,
    summary="更新訂單明細",
    description="更新訂單明細項目"
)
async def update_order_detail(
    order_id: str,
    detail_id: str,
    detail_update: OrderDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    detail = order_detail_crud.get_order_detail_by_id(db, detail_id)
    if not detail or detail.order_id != order_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單明細不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改此訂單明細"
        )
    
    # 檢查訂單狀態
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能修改待處理或已確認訂單的明細"
        )
    
    updated_detail = order_detail_crud.update_order_detail(db, detail, detail_update)
    
    return OrderDetailResponse(
        order_detail_id=updated_detail.order_detail_id,
        order_id=updated_detail.order_id,
        product_id=updated_detail.product_id,
        quantity=updated_detail.quantity,
        price_per_item=updated_detail.price_per_item,
        total_price=updated_detail.total_price,
        message=updated_detail.message,
        product_name=updated_detail.product.name if updated_detail.product else None,
        product_type="service" if updated_detail.product and updated_detail.product.is_service else "product"
    )


@router.delete(
    "/{order_id}/details/{detail_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除訂單明細",
    description="刪除訂單明細項目"
)
async def delete_order_detail(
    order_id: str,
    detail_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    detail = order_detail_crud.get_order_detail_by_id(db, detail_id)
    if not detail or detail.order_id != order_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單明細不存在"
        )
    
    # 檢查權限
    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除此訂單明細"
        )
    
    # 檢查訂單狀態
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能刪除待處理或已確認訂單的明細"
        )
    
    order_detail_crud.delete_order_detail(db, detail)


# 用戶特定端點
@router.get(
    "/user/{user_id}",
    response_model=List[OrderSummary],
    summary="獲取用戶訂單",
    description="獲取指定用戶的訂單列表"
)
async def get_user_orders(
    user_id: str,
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查權限
    if current_user.role != "admin" and user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看其他用戶的訂單"
        )

    orders, total = order_crud.get_orders(
        db, 
        skip=skip, 
        limit=limit,
        user_id=user_id,
        status=status
    )
    
    return [
        OrderSummary(
            order_id=order.order_id,
            user_id=order.user_id,
            appointment_id=order.appointment_id,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            status=order.status,
            created_at=order.created_at,
            item_count=len(order.details)
        ) for order in orders
    ]


# 統計端點
@router.get(
    "/statistics/overview",
    response_model=OrderStatistics,
    summary="獲取訂單統計",
    description="獲取訂單統計資料"
)
async def get_order_statistics(
    user_id: Optional[str] = Query(None, description="特定用戶 ID"),
    start_date: Optional[datetime] = Query(None, description="開始日期"),
    end_date: Optional[datetime] = Query(None, description="結束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 權限檢查
    if current_user.role != "admin":
        if user_id and user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限查看其他用戶的統計資料"
            )
        if not user_id:
            user_id = current_user.user_id

    stats = order_crud.get_order_statistics(
        db, 
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return OrderStatistics(**stats)