from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.timezone_utils import get_current_timestamp


class Appointment(Base):
    """
    預約資料庫模型。
    對應到資料庫中的 `Appointments` 表。
    """

    __tablename__ = "Appointments"

    appointment_id = Column(String(36), primary_key=True, index=True, comment="預約 ID")
    user_id = Column(
        String(36),
        ForeignKey("user.user_id"),
        nullable=False,
        comment="預約顧客的 ID"
    )
    stylist_id = Column(
        String(36),
        ForeignKey("user.user_id"),
        nullable=False,
        comment="負責服務的設計師 ID"
    )
    start_time = Column(DateTime, nullable=False, comment="預約開始時間")
    end_time = Column(DateTime, nullable=False, comment="預約結束時間")
    status = Column(String(50), nullable=False, comment="預約狀態")
    created_at = Column(
        DateTime, nullable=False, default=get_current_timestamp, comment="創建時間"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_current_timestamp,
        onupdate=get_current_timestamp,
        comment="更新時間",
    )

    # 關聯關係
    customer = relationship("User", foreign_keys=[user_id], back_populates="customer_appointments")
    stylist = relationship("User", foreign_keys=[stylist_id], back_populates="stylist_appointments")
    services = relationship("AppointmentService", back_populates="appointment")
    orders = relationship("Order", back_populates="appointment")


class AppointmentService(Base):
    """
    預約服務關聯資料庫模型。
    對應到資料庫中的 `AppointmentServices` 表。
    這是預約與服務項目之間的多對多關聯表。
    """

    __tablename__ = "AppointmentServices"

    appointment_id = Column(
        String(36),
        ForeignKey("Appointments.appointment_id", ondelete="CASCADE"),
        primary_key=True,
        comment="預約 ID"
    )
    product_id = Column(
        String(36),
        ForeignKey("Products.product_id", ondelete="CASCADE"),
        primary_key=True,
        comment="服務項目 ID（關聯到 Products 表）"
    )

    # 關聯關係
    appointment = relationship("Appointment", back_populates="services")
    product = relationship("Product")