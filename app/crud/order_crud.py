from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional, List, Tuple
from datetime import datetime

from app.models.order_models import Order, OrderDetail
from app.models.product_models import Product
from app.models.coupon_models import Coupon
from app.models.appointment_models import Appointment, AppointmentService
from app.schemas.order_schemas import (
    OrderCreate, 
    OrderUpdate,
    OrderDetailCreate,
    OrderDetailUpdate,
    OrderCalculation
)
from app.crud.coupon_crud import coupon_crud
import uuid


class OrderCRUD:
    """
    訂單資料的 CRUD (建立、讀取、更新、刪除) 操作。
    """

    def get_order_by_id(self, db: Session, order_id: str) -> Optional[Order]:
        """
        根據訂單 ID 獲取訂單。

        :param db: Session, 資料庫會話。
        :param order_id: str, 訂單 ID。
        :return: Optional[Order], 找到的訂單或 None。
        """
        return (
            db.query(Order)
            .options(
                joinedload(Order.details).joinedload(OrderDetail.product),
                joinedload(Order.coupon),
                joinedload(Order.appointment)
            )
            .filter(Order.order_id == order_id)
            .first()
        )

    def get_orders(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Order], int]:
        """
        獲取訂單列表（分頁和篩選）。

        :param db: Session, 資料庫會話。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param user_id: Optional[str], 客戶 ID 篩選。
        :param status: Optional[str], 狀態篩選。
        :param start_date: Optional[datetime], 開始日期篩選。
        :param end_date: Optional[datetime], 結束日期篩選。
        :return: Tuple[List[Order], int], 訂單列表和總數。
        """
        query = db.query(Order).options(
            joinedload(Order.details),
            joinedload(Order.coupon)
        )
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.status == status)
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
            
        total = query.count()
        orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        return orders, total

    def create_order(self, db: Session, order: OrderCreate) -> Order:
        """
        創建新訂單。

        :param db: Session, 資料庫會話。
        :param order: OrderCreate, 要創建的訂單數據。
        :return: Order, 創建的訂單。
        """
        # 計算訂單總金額
        subtotal = sum(detail.quantity * detail.price_per_item for detail in order.details)
        
        # 處理優惠券
        coupon_id = None
        discount_amount = 0
        
        if order.coupon_code:
            coupon_validation = coupon_crud.validate_coupon(
                db, order.coupon_code, subtotal
            )
            if coupon_validation.is_valid:
                coupon_id = coupon_validation.coupon_id
                discount_amount = coupon_validation.discount_amount
        
        final_amount = subtotal - discount_amount
        
        # 創建訂單
        db_order = Order(
            order_id=str(uuid.uuid4()),
            user_id=order.user_id,
            appointment_id=order.appointment_id,
            coupon_id=coupon_id,
            total_amount=subtotal,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status="pending",
            notes=order.notes
        )
        db.add(db_order)
        db.flush()  # 獲取訂單 ID
        
        # 創建訂單明細
        for detail in order.details:
            order_detail = OrderDetail(
                order_detail_id=str(uuid.uuid4()),
                order_id=db_order.order_id,
                product_id=detail.product_id,
                quantity=detail.quantity,
                price_per_item=detail.price_per_item,
                total_price=detail.quantity * detail.price_per_item,
                message=detail.message
            )
            db.add(order_detail)
        
        # 如果使用了優惠券，更新使用次數
        if coupon_id:
            coupon_crud.increment_usage_count(db, coupon_id)
        
        db.commit()
        db.refresh(db_order)
        return db_order

    def create_order_from_appointment(
        self, db: Session, appointment_id: str, user_id: str, coupon_code: Optional[str] = None, notes: Optional[str] = None
    ) -> Order:
        """
        從預約創建訂單。

        :param db: Session, 資料庫會話。
        :param appointment_id: str, 預約 ID。
        :param user_id: str, 客戶 ID。
        :param coupon_code: Optional[str], 優惠券代碼。
        :param notes: Optional[str], 訂單備註。
        :return: Order, 創建的訂單。
        """
        # 獲取預約的服務項目
        appointment_services = (
            db.query(AppointmentService, Product)
            .join(Product, AppointmentService.product_id == Product.product_id)
            .filter(
                AppointmentService.appointment_id == appointment_id,
                Product.is_active == True,
                Product.is_service == True
            )
            .all()
        )
        
        if not appointment_services:
            raise ValueError("預約沒有有效的服務項目")
        
        # 轉換為訂單明細
        order_details = []
        for _, product in appointment_services:
            order_details.append(OrderDetailCreate(
                product_id=product.product_id,
                quantity=1,
                price_per_item=product.price,
                message=f"來自預約 {appointment_id} 的服務項目"
            ))
        
        # 創建訂單
        order_create = OrderCreate(
            user_id=user_id,
            appointment_id=appointment_id,
            coupon_code=coupon_code,
            notes=notes,
            details=order_details
        )
        
        return self.create_order(db, order_create)

    def update_order(
        self, db: Session, order: Order, order_update: OrderUpdate
    ) -> Order:
        """
        更新訂單資訊。

        :param db: Session, 資料庫會話。
        :param order: Order, 要更新的訂單。
        :param order_update: OrderUpdate, 更新的數據。
        :return: Order, 更新後的訂單。
        """
        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        db.commit()
        db.refresh(order)
        return order

    def update_order_status(self, db: Session, order: Order, status: str) -> Order:
        """
        更新訂單狀態。

        :param db: Session, 資料庫會話。
        :param order: Order, 要更新的訂單。
        :param status: str, 新狀態。
        :return: Order, 更新後的訂單。
        """
        order.status = status
        db.commit()
        db.refresh(order)
        return order

    def apply_coupon_to_order(
        self, db: Session, order: Order, coupon_code: str
    ) -> Order:
        """
        為訂單應用優惠券。

        :param db: Session, 資料庫會話。
        :param order: Order, 訂單。
        :param coupon_code: str, 優惠券代碼。
        :return: Order, 更新後的訂單。
        """
        # 驗證優惠券
        coupon_validation = coupon_crud.validate_coupon(
            db, coupon_code, order.total_amount
        )
        
        if not coupon_validation.is_valid:
            raise ValueError(coupon_validation.error_message or "優惠券無效")
        
        # 如果訂單已有優惠券，先回退使用次數
        if order.coupon_id:
            coupon_crud.decrement_usage_count(db, order.coupon_id)
        
        # 應用新優惠券
        order.coupon_id = coupon_validation.coupon_id
        order.discount_amount = coupon_validation.discount_amount
        order.final_amount = order.total_amount - order.discount_amount
        
        # 增加新優惠券的使用次數
        coupon_crud.increment_usage_count(db, coupon_validation.coupon_id)
        
        db.commit()
        db.refresh(order)
        return order

    def remove_coupon_from_order(self, db: Session, order: Order) -> Order:
        """
        從訂單中移除優惠券。

        :param db: Session, 資料庫會話。
        :param order: Order, 訂單。
        :return: Order, 更新後的訂單。
        """
        if order.coupon_id:
            # 回退優惠券使用次數
            coupon_crud.decrement_usage_count(db, order.coupon_id)
            
            # 移除優惠券
            order.coupon_id = None
            order.discount_amount = 0
            order.final_amount = order.total_amount
            
            db.commit()
            db.refresh(order)
        
        return order

    def calculate_order_amount(self, db: Session, order_id: str) -> OrderCalculation:
        """
        計算訂單金額。

        :param db: Session, 資料庫會話。
        :param order_id: str, 訂單 ID。
        :return: OrderCalculation, 計算結果。
        """
        order = self.get_order_by_id(db, order_id)
        if not order:
            raise ValueError("訂單不存在")
        
        subtotal = sum(detail.total_price for detail in order.details)
        
        return OrderCalculation(
            subtotal=subtotal,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            coupon_applied=order.coupon.code if order.coupon else None
        )

    def delete_order(self, db: Session, order: Order) -> bool:
        """
        刪除訂單。

        :param db: Session, 資料庫會話。
        :param order: Order, 要刪除的訂單。
        :return: bool, 刪除成功返回 True。
        """
        # 如果有優惠券，回退使用次數
        if order.coupon_id:
            coupon_crud.decrement_usage_count(db, order.coupon_id)
        
        db.delete(order)
        db.commit()
        return True

    def get_order_statistics(
        self, 
        db: Session, 
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        獲取訂單統計資料。

        :param db: Session, 資料庫會話。
        :param user_id: Optional[str], 客戶 ID 篩選。
        :param start_date: Optional[datetime], 開始日期。
        :param end_date: Optional[datetime], 結束日期。
        :return: dict, 統計資料。
        """
        query = db.query(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        total_orders = query.count()
        total_revenue = query.with_entities(func.sum(Order.final_amount)).scalar() or 0
        pending_orders = query.filter(Order.status == 'pending').count()
        completed_orders = query.filter(Order.status == 'completed').count()
        cancelled_orders = query.filter(Order.status == 'cancelled').count()
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders
        }


class OrderDetailCRUD:
    """
    訂單明細的 CRUD 操作。
    """

    def get_order_details(self, db: Session, order_id: str) -> List[OrderDetail]:
        """
        獲取訂單的所有明細。

        :param db: Session, 資料庫會話。
        :param order_id: str, 訂單 ID。
        :return: List[OrderDetail], 訂單明細列表。
        """
        return (
            db.query(OrderDetail)
            .options(joinedload(OrderDetail.product))
            .filter(OrderDetail.order_id == order_id)
            .all()
        )

    def get_order_detail_by_id(self, db: Session, detail_id: str) -> Optional[OrderDetail]:
        """
        根據明細 ID 獲取訂單明細。

        :param db: Session, 資料庫會話。
        :param detail_id: str, 明細 ID。
        :return: Optional[OrderDetail], 找到的明細或 None。
        """
        return db.query(OrderDetail).filter(OrderDetail.order_detail_id == detail_id).first()

    def add_detail_to_order(
        self, db: Session, order_id: str, detail: OrderDetailCreate
    ) -> OrderDetail:
        """
        為訂單添加明細項目。

        :param db: Session, 資料庫會話。
        :param order_id: str, 訂單 ID。
        :param detail: OrderDetailCreate, 明細數據。
        :return: OrderDetail, 創建的明細。
        """
        db_detail = OrderDetail(
            order_detail_id=str(uuid.uuid4()),
            order_id=order_id,
            product_id=detail.product_id,
            quantity=detail.quantity,
            price_per_item=detail.price_per_item,
            total_price=detail.quantity * detail.price_per_item,
            message=detail.message
        )
        db.add(db_detail)
        
        # 更新訂單總金額
        self._update_order_amounts(db, order_id)
        
        db.commit()
        db.refresh(db_detail)
        return db_detail

    def update_order_detail(
        self, db: Session, detail: OrderDetail, detail_update: OrderDetailUpdate
    ) -> OrderDetail:
        """
        更新訂單明細。

        :param db: Session, 資料庫會話。
        :param detail: OrderDetail, 要更新的明細。
        :param detail_update: OrderDetailUpdate, 更新的數據。
        :return: OrderDetail, 更新後的明細。
        """
        update_data = detail_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(detail, field, value)
        
        # 重新計算小計
        detail.total_price = detail.quantity * detail.price_per_item
        
        # 更新訂單總金額
        self._update_order_amounts(db, detail.order_id)
        
        db.commit()
        db.refresh(detail)
        return detail

    def delete_order_detail(self, db: Session, detail: OrderDetail) -> bool:
        """
        刪除訂單明細。

        :param db: Session, 資料庫會話。
        :param detail: OrderDetail, 要刪除的明細。
        :return: bool, 刪除成功返回 True。
        """
        order_id = detail.order_id
        db.delete(detail)
        
        # 更新訂單總金額
        self._update_order_amounts(db, order_id)
        
        db.commit()
        return True

    def _update_order_amounts(self, db: Session, order_id: str):
        """
        更新訂單的總金額。

        :param db: Session, 資料庫會話。
        :param order_id: str, 訂單 ID。
        """
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return
        
        # 重新計算總金額
        subtotal = (
            db.query(func.sum(OrderDetail.total_price))
            .filter(OrderDetail.order_id == order_id)
            .scalar() or 0
        )
        
        order.total_amount = subtotal
        order.final_amount = subtotal - order.discount_amount


# 創建 CRUD 的單例實例
order_crud = OrderCRUD()
order_detail_crud = OrderDetailCRUD()