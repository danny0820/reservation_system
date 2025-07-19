from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import Optional, List, Tuple
from datetime import datetime

from app.models.appointment_models import Appointment, AppointmentService
from app.models.product_models import Product
from app.models.user_models import User
from app.schemas.appointment_schemas import (
    AppointmentCreate, 
    AppointmentUpdate,
    AppointmentServiceCreate,
    AppointmentCalculation
)
import uuid


class AppointmentCRUD:
    """
    預約資料的 CRUD (建立、讀取、更新、刪除) 操作。
    """

    def get_appointment_by_id(self, db: Session, appointment_id: str) -> Optional[Appointment]:
        """
        根據預約 ID 獲取預約。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :return: Optional[Appointment], 找到的預約或 None。
        """
        return db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()

    def get_appointments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Appointment], int]:
        """
        獲取預約列表（分頁和篩選）。

        :param db: Session, 資料庫會話。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param user_id: Optional[str], 客戶 ID 篩選。
        :param stylist_id: Optional[str], 設計師 ID 篩選。
        :param status: Optional[str], 狀態篩選。
        :param start_date: Optional[datetime], 開始日期篩選。
        :param end_date: Optional[datetime], 結束日期篩選。
        :return: Tuple[List[Appointment], int], 預約列表和總數。
        """
        query = db.query(Appointment)
        
        if user_id:
            query = query.filter(Appointment.user_id == user_id)
        if stylist_id:
            query = query.filter(Appointment.stylist_id == stylist_id)
        if status:
            query = query.filter(Appointment.status == status)
        if start_date:
            query = query.filter(Appointment.start_time >= start_date)
        if end_date:
            query = query.filter(Appointment.end_time <= end_date)
            
        total = query.count()
        appointments = query.order_by(Appointment.start_time).offset(skip).limit(limit).all()
        return appointments, total

    def create_appointment(self, db: Session, appointment: AppointmentCreate) -> Appointment:
        """
        創建新預約。

        :param db: Session, 資料庫會話。
        :param appointment: AppointmentCreate, 要創建的預約數據。
        :return: Appointment, 創建的預約。
        """
        db_appointment = Appointment(
            appointment_id=str(uuid.uuid4()),
            **appointment.model_dump()
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment

    def update_appointment(
        self, db: Session, appointment: Appointment, appointment_update: AppointmentUpdate
    ) -> Appointment:
        """
        更新預約資訊。

        :param db: Session, 資料庫會話。
        :param appointment: Appointment, 要更新的預約。
        :param appointment_update: AppointmentUpdate, 更新的數據。
        :return: Appointment, 更新後的預約。
        """
        update_data = appointment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        db.commit()
        db.refresh(appointment)
        return appointment

    def delete_appointment(self, db: Session, appointment: Appointment) -> bool:
        """
        刪除預約。

        :param db: Session, 資料庫會話。
        :param appointment: Appointment, 要刪除的預約。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(appointment)
        db.commit()
        return True

    def check_time_conflict(
        self,
        db: Session,
        stylist_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: Optional[str] = None
    ) -> bool:
        """
        檢查預約時間是否衝突。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param start_time: datetime, 開始時間。
        :param end_time: datetime, 結束時間。
        :param exclude_appointment_id: Optional[str], 排除的預約 ID（用於更新時）。
        :return: bool, 有衝突返回 True。
        """
        query = db.query(Appointment).filter(
            Appointment.stylist_id == stylist_id,
            Appointment.status.in_(['confirmed', 'in_progress']),
            and_(
                Appointment.start_time < end_time,
                Appointment.end_time > start_time
            )
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.appointment_id != exclude_appointment_id)
            
        return query.first() is not None


class AppointmentServiceCRUD:
    """
    預約服務關聯的 CRUD 操作。
    """

    def get_appointment_services(
        self, db: Session, appointment_id: str
    ) -> List[AppointmentService]:
        """
        獲取預約的所有服務項目。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :return: List[AppointmentService], 服務項目列表。
        """
        return (
            db.query(AppointmentService)
            .options(joinedload(AppointmentService.product))
            .filter(AppointmentService.appointment_id == appointment_id)
            .all()
        )

    def add_service_to_appointment(
        self, db: Session, appointment_id: str, service: AppointmentServiceCreate
    ) -> AppointmentService:
        """
        為預約添加服務項目。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :param service: AppointmentServiceCreate, 服務項目數據。
        :return: AppointmentService, 創建的服務關聯。
        """
        db_service = AppointmentService(
            appointment_id=appointment_id,
            product_id=service.product_id
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    def remove_service_from_appointment(
        self, db: Session, appointment_id: str, product_id: str
    ) -> bool:
        """
        從預約中移除服務項目。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :param product_id: str, 服務項目 ID。
        :return: bool, 刪除成功返回 True。
        """
        service = db.query(AppointmentService).filter(
            AppointmentService.appointment_id == appointment_id,
            AppointmentService.product_id == product_id
        ).first()
        
        if service:
            db.delete(service)
            db.commit()
            return True
        return False

    def get_appointment_calculation(
        self, db: Session, appointment_id: str
    ) -> Optional[AppointmentCalculation]:
        """
        計算預約的總時間和費用。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :return: Optional[AppointmentCalculation], 計算結果。
        """
        services = (
            db.query(AppointmentService, Product)
            .join(Product, AppointmentService.product_id == Product.product_id)
            .filter(
                AppointmentService.appointment_id == appointment_id,
                Product.is_active == True,
                Product.is_service == True
            )
            .all()
        )

        if not services:
            return None

        total_duration = 0
        total_price = 0
        service_list = []

        for appointment_service, product in services:
            duration = product.duration_time or 0
            price = product.price
            
            total_duration += duration
            total_price += price
            
            service_list.append({
                "appointment_id": appointment_id,
                "product_id": product.product_id,
                "product_name": product.name,
                "product_price": price,
                "duration_time": duration
            })

        return AppointmentCalculation(
            appointment_id=appointment_id,
            total_services=len(services),
            total_duration=total_duration,
            total_price=total_price,
            services=service_list
        )

    def bulk_add_services(
        self, db: Session, appointment_id: str, product_ids: List[str]
    ) -> List[AppointmentService]:
        """
        批量為預約添加服務項目。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :param product_ids: List[str], 服務項目 ID 列表。
        :return: List[AppointmentService], 創建的服務關聯列表。
        """
        services = []
        for product_id in product_ids:
            # 檢查是否已存在
            existing = db.query(AppointmentService).filter(
                AppointmentService.appointment_id == appointment_id,
                AppointmentService.product_id == product_id
            ).first()
            
            if not existing:
                service = AppointmentService(
                    appointment_id=appointment_id,
                    product_id=product_id
                )
                db.add(service)
                services.append(service)
        
        db.commit()
        for service in services:
            db.refresh(service)
        return services

    def clear_appointment_services(self, db: Session, appointment_id: str) -> bool:
        """
        清空預約的所有服務項目。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :return: bool, 成功返回 True。
        """
        db.query(AppointmentService).filter(
            AppointmentService.appointment_id == appointment_id
        ).delete()
        db.commit()
        return True

    def service_exists_in_appointment(
        self, db: Session, appointment_id: str, product_id: str
    ) -> bool:
        """
        檢查服務項目是否已在預約中。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :param product_id: str, 服務項目 ID。
        :return: bool, 存在返回 True。
        """
        return db.query(AppointmentService).filter(
            AppointmentService.appointment_id == appointment_id,
            AppointmentService.product_id == product_id
        ).first() is not None


# 創建 CRUD 的單例實例
appointment_crud = AppointmentCRUD()
appointment_service_crud = AppointmentServiceCRUD()