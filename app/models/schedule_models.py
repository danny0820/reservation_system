from sqlalchemy import Column, String, Integer, Time, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class StylistSchedules(Base):
    """
    設計師排班資料庫模型。
    對應到資料庫中的 `StylistSchedules` 表。
    """

    __tablename__ = "StylistSchedules"

    schedule_id = Column(String(36), primary_key=True, index=True, comment="排班 ID")
    stylist_id = Column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="設計師 ID",
    )
    day_of_week = Column(
        Integer, nullable=False, comment="星期幾 (0=週日, 1=週一, ..., 6=週六)"
    )
    start_time = Column(Time, nullable=False, comment="開始工作時間")
    end_time = Column(Time, nullable=False, comment="結束工作時間")
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


class StylistTimeOff(Base):
    """
    設計師請假資料庫模型。
    對應到資料庫中的 `StylistTimeOff` 表。
    """

    __tablename__ = "StylistTimeOff"

    time_off_id = Column(String(36), primary_key=True, index=True, comment="請假 ID")
    stylist_id = Column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="設計師 ID",
    )
    start_datetime = Column(DateTime, nullable=False, comment="請假開始時間")
    end_datetime = Column(DateTime, nullable=False, comment="請假結束時間")
    reason = Column(Text, nullable=True, comment="請假原因")
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        comment="請假狀態 (pending, approved, rejected)",
    )
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
