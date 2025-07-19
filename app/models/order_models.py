from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.timezone_utils import get_current_timestamp


class Order(Base):
    """
    訂單資料庫模型。
    對應到資料庫中的 `Order` 表。
    """

    __tablename__ = "Order"

    order_id = Column(String(36), primary_key=True, index=True, comment="訂單 ID")
    user_id = Column(
        String(36),
        ForeignKey("user.user_id"),
        nullable=False,
        comment="顧客 ID"
    )
    appointment_id = Column(
        String(36),
        ForeignKey("Appointments.appointment_id"),
        nullable=True,
        comment="預約 ID（可選）"
    )
    coupon_id = Column(
        String(36),
        ForeignKey("coupon.coupon_id"),
        nullable=True,
        comment="使用的優惠券 ID（可選）"
    )
    total_amount = Column(Integer, nullable=False, comment="訂單總金額（以分為單位）")
    discount_amount = Column(Integer, nullable=False, default=0, comment="折扣金額（以分為單位）")
    final_amount = Column(Integer, nullable=False, comment="最終金額（以分為單位）")
    status = Column(String(50), nullable=False, comment="訂單狀態")
    notes = Column(Text, nullable=True, comment="訂單備註")
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
    customer = relationship("User", back_populates="orders")
    appointment = relationship("Appointment", back_populates="orders")
    coupon = relationship("Coupon", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")


class OrderDetail(Base):
    """
    訂單明細資料庫模型。
    對應到資料庫中的 `Order_detail` 表。
    """

    __tablename__ = "Order_detail"

    order_detail_id = Column(String(36), primary_key=True, index=True, comment="訂單明細 ID")
    order_id = Column(
        String(36),
        ForeignKey("Order.order_id", ondelete="CASCADE"),
        nullable=False,
        comment="訂單 ID"
    )
    product_id = Column(
        String(36),
        ForeignKey("Products.product_id"),
        nullable=False,
        comment="商品 ID"
    )
    quantity = Column(Integer, nullable=False, comment="數量")
    price_per_item = Column(Integer, nullable=False, comment="單價（以分為單位）")
    total_price = Column(Integer, nullable=False, comment="小計（以分為單位）")
    message = Column(Text, nullable=True, comment="項目備註")

    # 關聯關係
    order = relationship("Order", back_populates="details")
    product = relationship("Product")