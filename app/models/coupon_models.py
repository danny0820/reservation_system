from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.timezone_utils import get_current_timestamp


class Coupon(Base):
    """
    優惠券資料庫模型。
    對應到資料庫中的 `coupon` 表。
    """

    __tablename__ = "coupon"

    coupon_id = Column(String(36), primary_key=True, index=True, comment="優惠券 ID")
    code = Column(String(255), unique=True, nullable=False, index=True, comment="優惠券代碼")
    name = Column(String(255), nullable=False, comment="優惠券名稱")
    description = Column(Text, nullable=True, comment="優惠券描述")
    discount_type = Column(String(50), nullable=False, comment="折扣類型 (percentage/fixed)")
    discount_value = Column(Integer, nullable=False, comment="折扣值")
    min_order_amount = Column(Integer, nullable=True, comment="最低消費金額（以分為單位）")
    max_discount_amount = Column(Integer, nullable=True, comment="最大折扣金額（以分為單位）")
    usage_limit = Column(Integer, nullable=True, comment="使用次數限制")
    used_count = Column(Integer, nullable=False, default=0, comment="已使用次數")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    start_at = Column(DateTime, nullable=True, comment="優惠券開始時間")
    end_at = Column(DateTime, nullable=True, comment="優惠券結束時間")
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
    orders = relationship("Order", back_populates="coupon")