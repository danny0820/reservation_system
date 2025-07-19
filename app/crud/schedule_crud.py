from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Dict
from datetime import datetime, time, date, timedelta

from app.models.schedule_models import StylistSchedules, StylistTimeOff
from app.schemas.schedule_schemas import (
    StylistSchedulesCreate,
    StylistSchedulesUpdate,
    StylistTimeOffCreate,
    StylistTimeOffUpdate,
    TimeOffStatus,
)
from app.utils.timezone_utils import ensure_utc8, UTC_8
import uuid


class ScheduleCRUD:
    """
    設計師排班和請假管理的 CRUD 操作。
    """

    # === 設計師排班管理 ===

    def get_schedule_by_id(
        self, db: Session, schedule_id: str
    ) -> Optional[StylistSchedules]:
        """
        根據排班 ID 獲取排班記錄。

        :param db: Session, 資料庫會話。
        :param schedule_id: str, 排班 ID。
        :return: Optional[StylistSchedules], 找到的排班記錄或 None。
        """
        return (
            db.query(StylistSchedules)
            .filter(StylistSchedules.schedule_id == schedule_id)
            .first()
        )

    def get_stylist_schedule_by_day(
        self, db: Session, stylist_id: str, day_of_week: int
    ) -> Optional[StylistSchedules]:
        """
        根據設計師 ID 和星期幾獲取排班。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param day_of_week: int, 星期幾 (0=週日, 1=週一, ..., 6=週六)。
        :return: Optional[StylistSchedules], 找到的排班記錄或 None。
        """
        return (
            db.query(StylistSchedules)
            .filter(
                and_(
                    StylistSchedules.stylist_id == stylist_id,
                    StylistSchedules.day_of_week == day_of_week,
                )
            )
            .first()
        )

    def get_stylist_all_schedules(
        self, db: Session, stylist_id: str
    ) -> List[StylistSchedules]:
        """
        獲取設計師的所有排班。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :return: List[StylistSchedules], 排班記錄列表。
        """
        return (
            db.query(StylistSchedules)
            .filter(StylistSchedules.stylist_id == stylist_id)
            .order_by(StylistSchedules.day_of_week)
            .all()
        )

    def create_or_update_schedule(
        self, db: Session, schedule_data: StylistSchedulesCreate
    ) -> StylistSchedules:
        """
        創建或更新設計師排班。

        :param db: Session, 資料庫會話。
        :param schedule_data: StylistSchedulesCreate, 排班數據。
        :return: StylistSchedules, 創建或更新的排班記錄。
        """
        existing_schedule = self.get_stylist_schedule_by_day(
            db, schedule_data.stylist_id, schedule_data.day_of_week
        )

        if existing_schedule:
            # 更新現有記錄
            setattr(existing_schedule, "start_time", schedule_data.start_time)
            setattr(existing_schedule, "end_time", schedule_data.end_time)
            db.commit()
            db.refresh(existing_schedule)
            return existing_schedule
        else:
            # 創建新記錄
            db_schedule = StylistSchedules(
                schedule_id=str(uuid.uuid4()), **schedule_data.dict()
            )
            db.add(db_schedule)
            db.commit()
            db.refresh(db_schedule)
            return db_schedule

    def update_schedule(
        self,
        db: Session,
        schedule: StylistSchedules,
        schedule_update: StylistSchedulesUpdate,
    ) -> StylistSchedules:
        """
        更新排班記錄。

        :param db: Session, 資料庫會話。
        :param schedule: StylistSchedules, 要更新的排班記錄。
        :param schedule_update: StylistSchedulesUpdate, 更新數據。
        :return: StylistSchedules, 更新後的排班記錄。
        """
        update_data = schedule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        db.commit()
        db.refresh(schedule)
        return schedule

    def delete_schedule(self, db: Session, schedule: StylistSchedules) -> bool:
        """
        刪除排班記錄。

        :param db: Session, 資料庫會話。
        :param schedule: StylistSchedules, 要刪除的排班記錄。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(schedule)
        db.commit()
        return True

    def get_all_stylists_schedules(
        self, db: Session, day_of_week: Optional[int] = None
    ) -> List[StylistSchedules]:
        """
        獲取所有設計師的排班。

        :param db: Session, 資料庫會話。
        :param day_of_week: Optional[int], 篩選特定星期幾。
        :return: List[StylistSchedules], 排班記錄列表。
        """
        query = db.query(StylistSchedules)
        if day_of_week is not None:
            query = query.filter(StylistSchedules.day_of_week == day_of_week)

        return query.order_by(
            StylistSchedules.stylist_id, StylistSchedules.day_of_week
        ).all()

    # === 設計師請假管理 ===

    def get_time_off_by_id(
        self, db: Session, time_off_id: str
    ) -> Optional[StylistTimeOff]:
        """
        根據請假 ID 獲取請假記錄。

        :param db: Session, 資料庫會話。
        :param time_off_id: str, 請假 ID。
        :return: Optional[StylistTimeOff], 找到的請假記錄或 None。
        """
        return (
            db.query(StylistTimeOff)
            .filter(StylistTimeOff.time_off_id == time_off_id)
            .first()
        )

    def get_stylist_time_offs(
        self,
        db: Session,
        stylist_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StylistTimeOff]:
        """
        獲取設計師的請假記錄。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param start_date: Optional[date], 查詢開始日期。
        :param end_date: Optional[date], 查詢結束日期。
        :return: List[StylistTimeOff], 請假記錄列表。
        """
        query = db.query(StylistTimeOff).filter(StylistTimeOff.stylist_id == stylist_id)

        if start_date:
            start_datetime_filter = ensure_utc8(datetime.combine(start_date, time.min))
            query = query.filter(StylistTimeOff.end_datetime >= start_datetime_filter)
        if end_date:
            end_datetime_filter = ensure_utc8(datetime.combine(end_date, time.max))
            query = query.filter(StylistTimeOff.start_datetime <= end_datetime_filter)

        return query.order_by(StylistTimeOff.start_datetime).all()

    def create_time_off(
        self, db: Session, time_off_data: StylistTimeOffCreate
    ) -> StylistTimeOff:
        """
        創建請假記錄。

        :param db: Session, 資料庫會話。
        :param time_off_data: StylistTimeOffCreate, 請假數據。
        :return: StylistTimeOff, 創建的請假記錄。
        """
        # 確保日期時間具有正確的時區信息
        time_off_dict = time_off_data.dict()
        time_off_dict['start_datetime'] = ensure_utc8(time_off_dict['start_datetime'])
        time_off_dict['end_datetime'] = ensure_utc8(time_off_dict['end_datetime'])
        
        db_time_off = StylistTimeOff(
            time_off_id=str(uuid.uuid4()), **time_off_dict
        )
        db.add(db_time_off)
        db.commit()
        db.refresh(db_time_off)
        return db_time_off

    def update_time_off(
        self,
        db: Session,
        time_off: StylistTimeOff,
        time_off_update: StylistTimeOffUpdate,
    ) -> StylistTimeOff:
        """
        更新請假記錄。

        :param db: Session, 資料庫會話。
        :param time_off: StylistTimeOff, 要更新的請假記錄。
        :param time_off_update: StylistTimeOffUpdate, 更新數據。
        :return: StylistTimeOff, 更新後的請假記錄。
        """
        update_data = time_off_update.dict(exclude_unset=True)
        # 確保日期時間字段具有正確的時區信息
        if 'start_datetime' in update_data and update_data['start_datetime'] is not None:
            update_data['start_datetime'] = ensure_utc8(update_data['start_datetime'])
        if 'end_datetime' in update_data and update_data['end_datetime'] is not None:
            update_data['end_datetime'] = ensure_utc8(update_data['end_datetime'])
            
        for field, value in update_data.items():
            setattr(time_off, field, value)

        db.commit()
        db.refresh(time_off)
        return time_off

# update_time_off_status 方法已移除，因為資料庫表中沒有 status 字段

    def delete_time_off(self, db: Session, time_off: StylistTimeOff) -> bool:
        """
        刪除請假記錄。

        :param db: Session, 資料庫會話。
        :param time_off: StylistTimeOff, 要刪除的請假記錄。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(time_off)
        db.commit()
        return True

    def get_all_time_offs(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StylistTimeOff]:
        """
        獲取所有設計師的請假記錄。

        :param db: Session, 資料庫會話。
        :param start_date: Optional[date], 查詢開始日期。
        :param end_date: Optional[date], 查詢結束日期。
        :return: List[StylistTimeOff], 請假記錄列表。
        """
        query = db.query(StylistTimeOff)

        if start_date:
            start_datetime_filter = ensure_utc8(datetime.combine(start_date, time.min))
            query = query.filter(StylistTimeOff.end_datetime >= start_datetime_filter)
        if end_date:
            end_datetime_filter = ensure_utc8(datetime.combine(end_date, time.max))
            query = query.filter(StylistTimeOff.start_datetime <= end_datetime_filter)

        return query.order_by(StylistTimeOff.start_datetime).all()

    # === 可用性檢查 ===

    def is_stylist_available(
        self, db: Session, stylist_id: str, check_datetime: datetime
    ) -> bool:
        """
        檢查設計師在指定時間是否可用。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param check_datetime: datetime, 檢查的時間點。
        :return: bool, 是否可用。
        """
        # 檢查是否有請假
        # 確保比較的 datetime 物件具有相同的時區信息
        check_datetime = ensure_utc8(check_datetime)
        time_offs = (
            db.query(StylistTimeOff)
            .filter(
                and_(
                    StylistTimeOff.stylist_id == stylist_id,
                    StylistTimeOff.start_datetime <= check_datetime,
                    StylistTimeOff.end_datetime >= check_datetime,
                )
            )
            .all()
        )

        if time_offs:
            return False

        # 檢查是否在工作時間內
        day_of_week = check_datetime.weekday()
        adjusted_day = 0 if day_of_week == 6 else day_of_week + 1

        schedule = self.get_stylist_schedule_by_day(db, stylist_id, adjusted_day)
        if not schedule:
            return False

        current_time = check_datetime.time()
        return schedule.start_time <= current_time <= schedule.end_time

    def get_stylist_available_slots(
        self, db: Session, stylist_id: str, target_date: date, slot_duration: int = 60
    ) -> List[Dict]:
        """
        獲取設計師在指定日期的可用時間段。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param target_date: date, 目標日期。
        :param slot_duration: int, 時間段長度（分鐘）。
        :return: List[Dict], 可用時間段列表。
        """
        day_of_week = target_date.weekday()
        adjusted_day = 0 if day_of_week == 6 else day_of_week + 1

        # 獲取當天排班
        schedule = self.get_stylist_schedule_by_day(db, stylist_id, adjusted_day)
        if not schedule:
            return []

        # 獲取當天請假
        time_offs = self.get_stylist_time_offs(
            db,
            stylist_id,
            start_date=target_date,
            end_date=target_date,
        )

        # 生成時間段
        available_slots = []
        current_time = ensure_utc8(datetime.combine(target_date, schedule.start_time))
        end_time = ensure_utc8(datetime.combine(target_date, schedule.end_time))

        while current_time + timedelta(minutes=slot_duration) <= end_time:
            slot_end = current_time + timedelta(minutes=slot_duration)

            # 檢查是否與請假衝突
            is_blocked = any(
                time_off.start_datetime <= current_time
                and time_off.end_datetime >= slot_end
                for time_off in time_offs
            )

            if not is_blocked:
                available_slots.append(
                    {
                        "start_time": current_time.strftime("%H:%M"),
                        "end_time": slot_end.strftime("%H:%M"),
                        "start_date": current_time,
                        "end_date": slot_end,
                    }
                )

            current_time += timedelta(minutes=slot_duration)

        return available_slots

    def check_schedule_conflicts(
        self,
        db: Session,
        stylist_id: str,
        day_of_week: int,
        start_time: time,
        end_time: time,
    ) -> Dict:
        """
        檢查新排班是否與現有安排衝突。

        :param db: Session, 資料庫會話。
        :param stylist_id: str, 設計師 ID。
        :param day_of_week: int, 星期幾。
        :param start_time: time, 開始時間。
        :param end_time: time, 結束時間。
        :return: Dict, 衝突檢查結果。
        """
        conflicts = []
        suggestions = []

        # 檢查是否與現有排班衝突
        existing_schedule = self.get_stylist_schedule_by_day(
            db, stylist_id, day_of_week
        )
        if existing_schedule:
            conflicts.append(
                {
                    "type": "existing_schedule",
                    "message": f"星期{day_of_week}已有排班：{existing_schedule.start_time}-{existing_schedule.end_time}",
                    "existing_start": existing_schedule.start_time.strftime("%H:%M"),
                    "existing_end": existing_schedule.end_time.strftime("%H:%M"),
                }
            )
            suggestions.append("建議更新現有排班時間或選擇其他星期")

        # TODO: 可以添加更多衝突檢查邏輯，如：
        # - 與其他設計師排班的資源衝突
        # - 與店面營業時間的衝突
        # - 與已預約服務的衝突

        return {
            "has_conflict": len(conflicts) > 0,
            "conflict_details": conflicts,
            "suggestions": suggestions,
        }


# 創建 ScheduleCRUD 的單例實例
schedule_crud = ScheduleCRUD()
