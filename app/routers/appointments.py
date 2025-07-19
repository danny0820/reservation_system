from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user_models import User
from app.models.appointment_models import Appointment
from app.schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentWithServicesResponse,
    AppointmentServiceCreate,
    AppointmentServiceResponse,
    AppointmentServiceBulkCreate,
    AppointmentCalculation,
    AppointmentStatusUpdate
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.appointment_crud import appointment_crud, appointment_service_crud

router = APIRouter()


# 預約管理端點
@router.get(
    "/",
    response_model=List[AppointmentResponse],
    summary="獲取預約列表",
    description="獲取預約列表，支援分頁和篩選"
)
async def get_appointments(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    user_id: Optional[str] = Query(None, description="客戶 ID 篩選"),
    stylist_id: Optional[str] = Query(None, description="設計師 ID 篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    start_date: Optional[datetime] = Query(None, description="開始日期篩選"),
    end_date: Optional[datetime] = Query(None, description="結束日期篩選"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 非管理員只能查看自己相關的預約
    if current_user.role != "admin":
        if current_user.role == "stylist":
            stylist_id = current_user.user_id
        else:  # customer
            user_id = current_user.user_id

    appointments, total = appointment_crud.get_appointments(
        db, 
        skip=skip, 
        limit=limit,
        user_id=user_id,
        stylist_id=stylist_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return appointments


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建新預約",
    description="創建新的預約"
)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 檢查是否為客戶本人或管理員
    if current_user.role == "customer" and appointment.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="客戶只能為自己創建預約"
        )
    
    # 檢查時間衝突
    if appointment_crud.check_time_conflict(
        db, appointment.stylist_id, appointment.start_time, appointment.end_time
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="該時段已有預約衝突"
        )
    
    return appointment_crud.create_appointment(db, appointment)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentWithServicesResponse,
    summary="獲取預約詳情",
    description="根據預約 ID 獲取預約詳情，包含服務項目"
)
async def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限查看此預約"
        )
    
    # 獲取服務項目
    services = appointment_service_crud.get_appointment_services(db, appointment_id)
    calculation = appointment_service_crud.get_appointment_calculation(db, appointment_id)
    
    return AppointmentWithServicesResponse(
        **appointment.__dict__,
        services=[
            AppointmentServiceResponse(
                appointment_id=service.appointment_id,
                product_id=service.product_id,
                product_name=service.product.name if service.product else None,
                product_price=service.product.price if service.product else None,
                duration_time=service.product.duration_time if service.product else None
            ) for service in services
        ],
        total_duration=calculation.total_duration if calculation else None,
        total_price=calculation.total_price if calculation else None
    )


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="更新預約",
    description="更新預約資訊"
)
async def update_appointment(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約"
            )
    
    # 如果更新時間，檢查衝突
    if appointment_update.start_time or appointment_update.end_time:
        start_time = appointment_update.start_time or appointment.start_time
        end_time = appointment_update.end_time or appointment.end_time
        
        if appointment_crud.check_time_conflict(
            db, appointment.stylist_id, start_time, end_time, appointment_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="該時段已有預約衝突"
            )
    
    return appointment_crud.update_appointment(db, appointment, appointment_update)


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
    summary="更新預約狀態",
    description="更新預約狀態"
)
async def update_appointment_status(
    appointment_id: str,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約狀態"
            )
    
    appointment_update = AppointmentUpdate(status=status_update.status)
    return appointment_crud.update_appointment(db, appointment, appointment_update)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除預約",
    description="刪除預約"
)
async def delete_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 只有管理員或預約客戶可以刪除
    if current_user.role != "admin" and appointment.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除此預約"
        )
    
    appointment_crud.delete_appointment(db, appointment)


# 預約服務管理端點
@router.get(
    "/{appointment_id}/services",
    response_model=List[AppointmentServiceResponse],
    summary="獲取預約服務",
    description="獲取預約的所有服務項目"
)
async def get_appointment_services(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限查看此預約的服務項目"
            )
    
    services = appointment_service_crud.get_appointment_services(db, appointment_id)
    return [
        AppointmentServiceResponse(
            appointment_id=service.appointment_id,
            product_id=service.product_id,
            product_name=service.product.name if service.product else None,
            product_price=service.product.price if service.product else None,
            duration_time=service.product.duration_time if service.product else None
        ) for service in services
    ]


@router.post(
    "/{appointment_id}/services",
    response_model=AppointmentServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增服務到預約",
    description="為預約新增服務項目"
)
async def add_service_to_appointment(
    appointment_id: str,
    service: AppointmentServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約的服務項目"
            )
    
    # 檢查服務是否已存在
    if appointment_service_crud.service_exists_in_appointment(db, appointment_id, service.product_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="此服務項目已在預約中"
        )
    
    created_service = appointment_service_crud.add_service_to_appointment(db, appointment_id, service)
    
    return AppointmentServiceResponse(
        appointment_id=created_service.appointment_id,
        product_id=created_service.product_id,
        product_name=created_service.product.name if created_service.product else None,
        product_price=created_service.product.price if created_service.product else None,
        duration_time=created_service.product.duration_time if created_service.product else None
    )


@router.post(
    "/{appointment_id}/services/bulk",
    response_model=List[AppointmentServiceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="批量新增服務到預約",
    description="批量為預約新增多個服務項目"
)
async def bulk_add_services_to_appointment(
    appointment_id: str,
    services: AppointmentServiceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約的服務項目"
            )
    
    created_services = appointment_service_crud.bulk_add_services(db, appointment_id, services.product_ids)
    
    return [
        AppointmentServiceResponse(
            appointment_id=service.appointment_id,
            product_id=service.product_id,
            product_name=service.product.name if service.product else None,
            product_price=service.product.price if service.product else None,
            duration_time=service.product.duration_time if service.product else None
        ) for service in created_services
    ]


@router.delete(
    "/{appointment_id}/services/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="移除預約服務",
    description="從預約中移除服務項目"
)
async def remove_service_from_appointment(
    appointment_id: str,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約的服務項目"
            )
    
    success = appointment_service_crud.remove_service_from_appointment(db, appointment_id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服務項目不在此預約中"
        )


@router.get(
    "/{appointment_id}/calculation",
    response_model=AppointmentCalculation,
    summary="獲取預約費用計算",
    description="計算預約的總時間和費用"
)
async def get_appointment_calculation(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限查看此預約的計算結果"
            )
    
    calculation = appointment_service_crud.get_appointment_calculation(db, appointment_id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約沒有服務項目"
        )
    
    return calculation


@router.delete(
    "/{appointment_id}/services",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="清空預約服務",
    description="清空預約的所有服務項目"
)
async def clear_appointment_services(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    appointment = appointment_crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="預約不存在"
        )
    
    # 檢查權限
    if (current_user.role == "customer" and appointment.user_id != current_user.user_id) or \
       (current_user.role == "stylist" and appointment.stylist_id != current_user.user_id):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限修改此預約的服務項目"
            )
    
    appointment_service_crud.clear_appointment_services(db, appointment_id)