from sqlalchemy import Column, String, Integer, Boolean, Time, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class StoreBusinessHours(Base):
    """
    店面營業時間資料庫模型。
    對應到資料庫中的 `StoreBusinessHours` 表。
    """

    __tablename__ = "StoreBusinessHours"

    hour_id = Column(String(36), primary_key=True, index=True, comment="營業時間 ID")
    day_of_week = Column(
        Integer, nullable=False, comment="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    )
    open_time = Column(Time, nullable=True, comment="開始營業時間")
    close_time = Column(Time, nullable=True, comment="結束營業時間")
    is_closed = Column(
        Boolean, nullable=False, default=False, comment="當天是否固定公休"
    )


class StoreClosures(Base):
    """
    店面臨時休業資料庫模型。
    對應到資料庫中的 `StoreClosures` 表。
    """

    __tablename__ = "StoreClosures"

    closure_id = Column(String(36), primary_key=True, index=True, comment="休業 ID")
    start_datetime = Column(DateTime, nullable=False, comment="休業開始時間")
    end_datetime = Column(DateTime, nullable=False, comment="休業結束時間")
    reason = Column(Text, nullable=True, comment="休業原因")
    created_at = Column(
        DateTime, nullable=False, default=func.now(), comment="創建時間"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="更新時間",
    )
