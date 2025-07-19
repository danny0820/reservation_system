from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, List, Tuple
from datetime import datetime

from app.models.coupon_models import Coupon
from app.schemas.coupon_schemas import (
    CouponCreate, 
    CouponUpdate,
    CouponValidationResult,
    BulkCouponCreate
)
import uuid


class CouponCRUD:
    """
    優惠券資料的 CRUD (建立、讀取、更新、刪除) 操作。
    """

    def get_coupon_by_id(self, db: Session, coupon_id: str) -> Optional[Coupon]:
        """
        根據優惠券 ID 獲取優惠券。

        :param db: Session, 資料庫會話。
        :param coupon_id: str, 優惠券 ID。
        :return: Optional[Coupon], 找到的優惠券或 None。
        """
        return db.query(Coupon).filter(Coupon.coupon_id == coupon_id).first()

    def get_coupon_by_code(self, db: Session, code: str) -> Optional[Coupon]:
        """
        根據優惠券代碼獲取優惠券。

        :param db: Session, 資料庫會話。
        :param code: str, 優惠券代碼。
        :return: Optional[Coupon], 找到的優惠券或 None。
        """
        return db.query(Coupon).filter(Coupon.code == code).first()

    def get_coupons(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        discount_type: Optional[str] = None,
    ) -> Tuple[List[Coupon], int]:
        """
        獲取優惠券列表（分頁和篩選）。

        :param db: Session, 資料庫會話。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param is_active: Optional[bool], 是否啟用篩選。
        :param discount_type: Optional[str], 折扣類型篩選。
        :return: Tuple[List[Coupon], int], 優惠券列表和總數。
        """
        query = db.query(Coupon)
        
        if is_active is not None:
            query = query.filter(Coupon.is_active == is_active)
        if discount_type:
            query = query.filter(Coupon.discount_type == discount_type)
            
        total = query.count()
        coupons = query.order_by(desc(Coupon.created_at)).offset(skip).limit(limit).all()
        return coupons, total

    def get_available_coupons(
        self, db: Session, order_amount: int, skip: int = 0, limit: int = 100
    ) -> List[Coupon]:
        """
        獲取可用的優惠券列表。

        :param db: Session, 資料庫會話。
        :param order_amount: int, 訂單金額（以分為單位）。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :return: List[Coupon], 可用的優惠券列表。
        """
        current_time = datetime.utcnow()
        
        query = db.query(Coupon).filter(
            Coupon.is_active == True,
            and_(
                Coupon.start_at.is_(None) | (Coupon.start_at <= current_time),
                Coupon.end_at.is_(None) | (Coupon.end_at >= current_time)
            ),
            and_(
                Coupon.min_order_amount.is_(None) | (Coupon.min_order_amount <= order_amount),
                Coupon.usage_limit.is_(None) | (Coupon.used_count < Coupon.usage_limit)
            )
        )
        
        return query.offset(skip).limit(limit).all()

    def create_coupon(self, db: Session, coupon: CouponCreate) -> Coupon:
        """
        創建新優惠券。

        :param db: Session, 資料庫會話。
        :param coupon: CouponCreate, 要創建的優惠券數據。
        :return: Coupon, 創建的優惠券。
        """
        db_coupon = Coupon(
            coupon_id=str(uuid.uuid4()),
            **coupon.model_dump()
        )
        db.add(db_coupon)
        db.commit()
        db.refresh(db_coupon)
        return db_coupon

    def bulk_create_coupons(self, db: Session, bulk_coupon: BulkCouponCreate) -> List[Coupon]:
        """
        批量創建優惠券。

        :param db: Session, 資料庫會話。
        :param bulk_coupon: BulkCouponCreate, 批量創建數據。
        :return: List[Coupon], 創建的優惠券列表。
        """
        coupons = []
        for i in range(1, bulk_coupon.count + 1):
            code = f"{bulk_coupon.base_code}{i:04d}"  # 例如: SUMMER0001
            name = bulk_coupon.name_template.format(index=i)
            
            coupon_data = CouponCreate(
                code=code,
                name=name,
                discount_type=bulk_coupon.discount_type,
                discount_value=bulk_coupon.discount_value,
                min_order_amount=bulk_coupon.min_order_amount,
                max_discount_amount=bulk_coupon.max_discount_amount,
                usage_limit=bulk_coupon.usage_limit,
                start_at=bulk_coupon.start_at,
                end_at=bulk_coupon.end_at
            )
            
            db_coupon = Coupon(
                coupon_id=str(uuid.uuid4()),
                **coupon_data.model_dump()
            )
            db.add(db_coupon)
            coupons.append(db_coupon)
        
        db.commit()
        for coupon in coupons:
            db.refresh(coupon)
        return coupons

    def update_coupon(
        self, db: Session, coupon: Coupon, coupon_update: CouponUpdate
    ) -> Coupon:
        """
        更新優惠券資訊。

        :param db: Session, 資料庫會話。
        :param coupon: Coupon, 要更新的優惠券。
        :param coupon_update: CouponUpdate, 更新的數據。
        :return: Coupon, 更新後的優惠券。
        """
        update_data = coupon_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(coupon, field, value)
        db.commit()
        db.refresh(coupon)
        return coupon

    def update_coupon_status(self, db: Session, coupon: Coupon, is_active: bool) -> Coupon:
        """
        更新優惠券啟用狀態。

        :param db: Session, 資料庫會話。
        :param coupon: Coupon, 要更新的優惠券。
        :param is_active: bool, 啟用狀態。
        :return: Coupon, 更新後的優惠券。
        """
        coupon.is_active = is_active
        db.commit()
        db.refresh(coupon)
        return coupon

    def delete_coupon(self, db: Session, coupon: Coupon) -> bool:
        """
        刪除優惠券。

        :param db: Session, 資料庫會話。
        :param coupon: Coupon, 要刪除的優惠券。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(coupon)
        db.commit()
        return True

    def validate_coupon(
        self, db: Session, coupon_code: str, order_amount: int
    ) -> CouponValidationResult:
        """
        驗證優惠券是否可用並計算折扣。

        :param db: Session, 資料庫會話。
        :param coupon_code: str, 優惠券代碼。
        :param order_amount: int, 訂單金額（以分為單位）。
        :return: CouponValidationResult, 驗證結果。
        """
        coupon = self.get_coupon_by_code(db, coupon_code)
        
        if not coupon:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message="優惠券不存在"
            )
        
        if not coupon.is_active:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message="優惠券已停用"
            )
        
        current_time = datetime.utcnow()
        
        # 檢查有效期限
        if coupon.start_at and current_time < coupon.start_at:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message="優惠券尚未生效"
            )
        
        if coupon.end_at and current_time > coupon.end_at:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message="優惠券已過期"
            )
        
        # 檢查使用次數限制
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message="優惠券使用次數已達上限"
            )
        
        # 檢查最低消費金額
        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            return CouponValidationResult(
                is_valid=False,
                final_amount=order_amount,
                error_message=f"訂單金額需達 {coupon.min_order_amount / 100:.2f} 元才能使用此優惠券"
            )
        
        # 計算折扣金額
        discount_amount = self._calculate_discount(coupon, order_amount)
        final_amount = order_amount - discount_amount
        
        return CouponValidationResult(
            is_valid=True,
            coupon_id=coupon.coupon_id,
            coupon_name=coupon.name,
            discount_amount=discount_amount,
            final_amount=final_amount
        )

    def _calculate_discount(self, coupon: Coupon, order_amount: int) -> int:
        """
        計算折扣金額。

        :param coupon: Coupon, 優惠券。
        :param order_amount: int, 訂單金額（以分為單位）。
        :return: int, 折扣金額（以分為單位）。
        """
        if coupon.discount_type == "percentage":
            # 百分比折扣（discount_value 以 basis points 表示，例如 1000 = 10%）
            discount_amount = (order_amount * coupon.discount_value) // 10000
            
            # 檢查最大折扣金額限制
            if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
                discount_amount = coupon.max_discount_amount
                
        elif coupon.discount_type == "fixed":
            # 固定金額折扣
            discount_amount = coupon.discount_value
            
            # 折扣不能超過訂單金額
            if discount_amount > order_amount:
                discount_amount = order_amount
        else:
            discount_amount = 0
        
        return discount_amount

    def increment_usage_count(self, db: Session, coupon_id: str) -> bool:
        """
        增加優惠券使用次數。

        :param db: Session, 資料庫會話。
        :param coupon_id: str, 優惠券 ID。
        :return: bool, 成功返回 True。
        """
        coupon = self.get_coupon_by_id(db, coupon_id)
        if coupon:
            coupon.used_count += 1
            db.commit()
            return True
        return False

    def decrement_usage_count(self, db: Session, coupon_id: str) -> bool:
        """
        減少優惠券使用次數（用於取消訂單時）。

        :param db: Session, 資料庫會話。
        :param coupon_id: str, 優惠券 ID。
        :return: bool, 成功返回 True。
        """
        coupon = self.get_coupon_by_id(db, coupon_id)
        if coupon and coupon.used_count > 0:
            coupon.used_count -= 1
            db.commit()
            return True
        return False

    def get_coupon_statistics(self, db: Session) -> dict:
        """
        獲取優惠券統計資料。

        :param db: Session, 資料庫會話。
        :return: dict, 統計資料。
        """
        total_coupons = db.query(Coupon).count()
        active_coupons = db.query(Coupon).filter(Coupon.is_active == True).count()
        used_coupons = db.query(Coupon).filter(Coupon.used_count > 0).count()
        
        # 計算總折扣金額需要從訂單表查詢，這裡暫時返回 0
        total_discount_amount = 0
        
        # 查找最常使用的優惠券
        most_used_coupon_result = (
            db.query(Coupon.code)
            .filter(Coupon.used_count > 0)
            .order_by(desc(Coupon.used_count))
            .first()
        )
        most_used_coupon = most_used_coupon_result[0] if most_used_coupon_result else None
        
        return {
            "total_coupons": total_coupons,
            "active_coupons": active_coupons,
            "used_coupons": used_coupons,
            "total_discount_amount": total_discount_amount,
            "most_used_coupon": most_used_coupon
        }

    def get_expiring_coupons(
        self, db: Session, days_ahead: int = 7
    ) -> List[Coupon]:
        """
        獲取即將過期的優惠券。

        :param db: Session, 資料庫會話。
        :param days_ahead: int, 提前天數。
        :return: List[Coupon], 即將過期的優惠券列表。
        """
        from datetime import timedelta
        
        expiry_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return (
            db.query(Coupon)
            .filter(
                Coupon.is_active == True,
                Coupon.end_at.isnot(None),
                Coupon.end_at <= expiry_date,
                Coupon.end_at > datetime.utcnow()
            )
            .all()
        )

    def cleanup_expired_coupons(self, db: Session) -> int:
        """
        清理過期的優惠券（停用）。

        :param db: Session, 資料庫會話。
        :return: int, 停用的優惠券數量。
        """
        current_time = datetime.utcnow()
        
        expired_coupons = db.query(Coupon).filter(
            Coupon.is_active == True,
            Coupon.end_at.isnot(None),
            Coupon.end_at < current_time
        ).all()
        
        count = 0
        for coupon in expired_coupons:
            coupon.is_active = False
            count += 1
        
        db.commit()
        return count


# 創建 CouponCRUD 的單例實例
coupon_crud = CouponCRUD()