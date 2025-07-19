from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base
from app.utils.timezone_utils import get_current_timestamp


class Product(Base):
    """
    商品/服務資料庫模型。
    對應到資料庫中的 `Products` 表。
    """

    __tablename__ = "Products"

    product_id = Column(String(36), primary_key=True, index=True, comment="商品 ID")
    name = Column(String(150), nullable=False, comment="商品/服務名稱")
    description = Column(Text, nullable=True, comment="詳細描述")
    price = Column(Integer, nullable=False, comment="價格（以分為單位）")
    duration_time = Column(Integer, nullable=True, comment="服務耗時（分鐘）")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="庫存數量")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否啟用")
    is_service = Column(
        Boolean, nullable=False, default=False, comment="是否為服務項目"
    )
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
