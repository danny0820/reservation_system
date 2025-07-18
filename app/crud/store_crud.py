from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict
from datetime import datetime, time, date, timedelta

from app.models.store_models import StoreBusinessHours, StoreClosures
from app.schemas.store_schemas import (
    StoreBusinessHoursCreate,
    StoreBusinessHoursUpdate,
    StoreClosuresCreate,
    StoreClosuresUpdate,
)
import uuid


class StoreCRUD:
    """
    店面營業時間和休業管理的 CRUD 操作。
    """

    # === 營業時間管理 ===

    def get_business_hours_by_day(
        self, db: Session, day_of_week: int
    ) -> Optional[StoreBusinessHours]:
        """
        根據星期幾獲取營業時間。

        :param db: Session, 資料庫會話。
        :param day_of_week: int, 星期幾 (0=週日, 1=週一, ..., 6=週六)。
        :return: Optional[StoreBusinessHours], 找到的營業時間或 None。
        """
        return (
            db.query(StoreBusinessHours)
            .filter(StoreBusinessHours.day_of_week == day_of_week)
            .first()
        )

    def get_all_business_hours(self, db: Session) -> List[StoreBusinessHours]:
        """
        獲取所有營業時間設定。

        :param db: Session, 資料庫會話。
        :return: List[StoreBusinessHours], 營業時間列表。
        """
        return (
            db.query(StoreBusinessHours).order_by(StoreBusinessHours.day_of_week).all()
        )

    def create_or_update_business_hours(
        self, db: Session, day_of_week: int, hours_data: StoreBusinessHoursCreate
    ) -> StoreBusinessHours:
        """
        創建或更新營業時間。

        :param db: Session, 資料庫會話。
        :param day_of_week: int, 星期幾。
        :param hours_data: StoreBusinessHoursCreate, 營業時間數據。
        :return: StoreBusinessHours, 創建或更新的營業時間。
        """
        existing_hours = self.get_business_hours_by_day(db, day_of_week)

        if existing_hours:
            # 更新現有記錄
            for field, value in hours_data.dict().items():
                setattr(existing_hours, field, value)
            db.commit()
            db.refresh(existing_hours)
            return existing_hours
        else:
            # 創建新記錄
            db_hours = StoreBusinessHours(
                hour_id=str(uuid.uuid4()), **hours_data.dict()
            )
            db.add(db_hours)
            db.commit()
            db.refresh(db_hours)
            return db_hours

    def update_business_hours(
        self, db: Session, day_of_week: int, hours_update: StoreBusinessHoursUpdate
    ) -> Optional[StoreBusinessHours]:
        """
        更新指定日期的營業時間。

        :param db: Session, 資料庫會話。
        :param day_of_week: int, 星期幾。
        :param hours_update: StoreBusinessHoursUpdate, 更新數據。
        :return: Optional[StoreBusinessHours], 更新後的營業時間。
        """
        hours = self.get_business_hours_by_day(db, day_of_week)
        if not hours:
            return None

        update_data = hours_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hours, field, value)

        db.commit()
        db.refresh(hours)
        return hours

    def get_weekly_business_hours(
        self, db: Session
    ) -> Dict[str, Optional[StoreBusinessHours]]:
        """
        獲取一週的營業時間。

        :param db: Session, 資料庫會話。
        :return: Dict[str, Optional[StoreBusinessHours]], 一週營業時間字典。
        """
        hours_list = self.get_all_business_hours(db)
        hours_dict = {h.day_of_week: h for h in hours_list}

        week_days: Dict[str, Optional[StoreBusinessHours]] = {
            "sunday": hours_dict.get(0),
            "monday": hours_dict.get(1),
            "tuesday": hours_dict.get(2),
            "wednesday": hours_dict.get(3),
            "thursday": hours_dict.get(4),
            "friday": hours_dict.get(5),
            "saturday": hours_dict.get(6),
        }

        return week_days

    # === 臨時休業管理 ===

    def get_closure_by_id(
        self, db: Session, closure_id: str
    ) -> Optional[StoreClosures]:
        """
        根據休業 ID 獲取休業記錄。

        :param db: Session, 資料庫會話。
        :param closure_id: str, 休業 ID。
        :return: Optional[StoreClosures], 找到的休業記錄或 None。
        """
        return (
            db.query(StoreClosures)
            .filter(StoreClosures.closure_id == closure_id)
            .first()
        )

    def get_closures(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StoreClosures]:
        """
        獲取休業記錄列表。

        :param db: Session, 資料庫會話。
        :param start_date: Optional[date], 查詢開始日期。
        :param end_date: Optional[date], 查詢結束日期。
        :return: List[StoreClosures], 休業記錄列表。
        """
        query = db.query(StoreClosures)

        if start_date:
            query = query.filter(
                StoreClosures.end_datetime >= datetime.combine(start_date, time.min)
            )
        if end_date:
            query = query.filter(
                StoreClosures.start_datetime <= datetime.combine(end_date, time.max)
            )

        return query.order_by(StoreClosures.start_datetime).all()

    def create_closure(
        self, db: Session, closure: StoreClosuresCreate
    ) -> StoreClosures:
        """
        創建休業記錄。

        :param db: Session, 資料庫會話。
        :param closure: StoreClosuresCreate, 休業數據。
        :return: StoreClosures, 創建的休業記錄。
        """
        db_closure = StoreClosures(closure_id=str(uuid.uuid4()), **closure.dict())
        db.add(db_closure)
        db.commit()
        db.refresh(db_closure)
        return db_closure

    def update_closure(
        self, db: Session, closure: StoreClosures, closure_update: StoreClosuresUpdate
    ) -> StoreClosures:
        """
        更新休業記錄。

        :param db: Session, 資料庫會話。
        :param closure: StoreClosures, 要更新的休業記錄。
        :param closure_update: StoreClosuresUpdate, 更新數據。
        :return: StoreClosures, 更新後的休業記錄。
        """
        update_data = closure_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(closure, field, value)

        db.commit()
        db.refresh(closure)
        return closure

    def delete_closure(self, db: Session, closure: StoreClosures) -> bool:
        """
        刪除休業記錄。

        :param db: Session, 資料庫會話。
        :param closure: StoreClosures, 要刪除的休業記錄。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(closure)
        db.commit()
        return True

    def get_active_closures(
        self, db: Session, check_datetime: Optional[datetime] = None
    ) -> List[StoreClosures]:
        """
        獲取指定時間點的有效休業記錄。

        :param db: Session, 資料庫會話。
        :param check_datetime: Optional[datetime], 檢查的時間點，預設為當前時間。
        :return: List[StoreClosures], 有效的休業記錄列表。
        """
        if check_datetime is None:
            check_datetime = datetime.now()

        return (
            db.query(StoreClosures)
            .filter(
                and_(
                    StoreClosures.start_datetime <= check_datetime,
                    StoreClosures.end_datetime >= check_datetime,
                )
            )
            .all()
        )

    # === 營業狀態查詢 ===

    def is_store_open(
        self, db: Session, check_datetime: Optional[datetime] = None
    ) -> bool:
        """
        檢查店面是否營業中。

        :param db: Session, 資料庫會話。
        :param check_datetime: Optional[datetime], 檢查的時間點，預設為當前時間。
        :return: bool, 是否營業中。
        """
        if check_datetime is None:
            check_datetime = datetime.now()

        # 檢查是否有臨時休業
        active_closures = self.get_active_closures(db, check_datetime)
        if active_closures:
            return False

        # 檢查當天營業時間
        day_of_week = check_datetime.weekday()
        # Python weekday(): 0=週一, 6=週日
        # 我們的系統: 0=週日, 1=週一, ..., 6=週六
        adjusted_day = 0 if day_of_week == 6 else day_of_week + 1

        business_hours = self.get_business_hours_by_day(db, adjusted_day)
        if not business_hours or business_hours.is_closed:
            return False

        current_time = check_datetime.time()
        return business_hours.open_time <= current_time <= business_hours.close_time

    def get_next_open_time(
        self, db: Session, from_datetime: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        獲取下次營業時間。

        :param db: Session, 資料庫會話。
        :param from_datetime: Optional[datetime], 從哪個時間點開始查找，預設為當前時間。
        :return: Optional[datetime], 下次營業時間。
        """
        if from_datetime is None:
            from_datetime = datetime.now()

        # 檢查接下來7天的營業時間
        for i in range(7):
            check_date = from_datetime.date() + timedelta(days=i)
            check_datetime = (
                datetime.combine(check_date, time.min) if i > 0 else from_datetime
            )

            day_of_week = check_date.weekday()
            adjusted_day = 0 if day_of_week == 6 else day_of_week + 1

            business_hours = self.get_business_hours_by_day(db, adjusted_day)
            if (
                business_hours
                and not business_hours.is_closed
                and business_hours.open_time
            ):
                next_open = datetime.combine(check_date, business_hours.open_time)

                # 檢查是否有休業衝突
                closures = self.get_active_closures(db, next_open)
                if not closures and next_open > from_datetime:
                    return next_open

        return None


# 創建 StoreCRUD 的單例實例
store_crud = StoreCRUD()
