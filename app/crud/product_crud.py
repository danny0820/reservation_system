from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List

from app.models.product_models import Product
from app.schemas.product_schemas import ProductCreate, ProductUpdate
import uuid


class ProductCRUD:
    """
    商品/服務資料的 CRUD (建立、讀取、更新、刪除) 操作。
    """

    def get_product_by_id(self, db: Session, product_id: str) -> Optional[Product]:
        """
        根據商品 ID 獲取商品。

        :param db: Session, 資料庫會話。
        :param product_id: str, 商品 ID。
        :return: Optional[Product], 找到的商品或 None。
        """
        return db.query(Product).filter(Product.product_id == product_id).first()

    def get_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ):
        """
        獲取商品列表（分頁）。

        :param db: Session, 資料庫會話。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param is_active: Optional[bool], 是否只取得啟用的商品。
        :return: Tuple[List[Product], int], 商品列表和總數。
        """
        query = db.query(Product)
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        return products, total

    def get_products_by_type(
        self,
        db: Session,
        is_service: bool,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Product]:
        """
        根據類型獲取商品（服務或實體商品）。

        :param db: Session, 資料庫會話。
        :param is_service: bool, 是否為服務項目。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param is_active: Optional[bool], 是否只取得啟用的商品。
        :return: List[Product], 商品列表。
        """
        query = db.query(Product).filter(Product.is_service == is_service)
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def search_products(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ):
        """
        搜尋商品（根據名稱或描述）。

        :param db: Session, 資料庫會話。
        :param query: str, 搜尋關鍵字。
        :param skip: int, 跳過的記錄數。
        :param limit: int, 返回的最大記錄數。
        :param is_active: Optional[bool], 是否只取得啟用的商品。
        :return: Tuple[List[Product], int], 符合條件的商品列表和總數。
        """
        search_pattern = f"%{query}%"
        db_query = db.query(Product).filter(
            (Product.name.like(search_pattern))
            | (Product.description.like(search_pattern))
        )
        if is_active is not None:
            db_query = db_query.filter(Product.is_active == is_active)
        
        total = db_query.count()
        products = db_query.offset(skip).limit(limit).all()
        return products, total

    def create_product(self, db: Session, product: ProductCreate) -> Product:
        """
        創建新商品。

        :param db: Session, 資料庫會話。
        :param product: ProductCreate, 要創建的商品數據。
        :return: Product, 創建的商品。
        """
        db_product = Product(product_id=str(uuid.uuid4()), **product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def update_product(
        self, db: Session, product: Product, product_update: ProductUpdate
    ) -> Product:
        """
        更新商品資訊。

        :param db: Session, 資料庫會話。
        :param product: Product, 要更新的商品。
        :param product_update: ProductUpdate, 更新的數據。
        :return: Product, 更新後的商品。
        """
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return product

    def update_product_status(
        self, db: Session, product: Product, is_active: bool
    ) -> Product:
        """
        更新商品啟用狀態。

        :param db: Session, 資料庫會話。
        :param product: Product, 要更新的商品。
        :param is_active: bool, 啟用狀態。
        :return: Product, 更新後的商品。
        """
        product.is_active = is_active
        db.commit()
        db.refresh(product)
        return product

    def update_product_stock(
        self, db: Session, product: Product, stock_quantity: int
    ) -> Product:
        """
        更新商品庫存。

        :param db: Session, 資料庫會話。
        :param product: Product, 要更新的商品。
        :param stock_quantity: int, 新庫存數量。
        :return: Product, 更新後的商品。
        """
        product.stock_quantity = stock_quantity
        db.commit()
        db.refresh(product)
        return product

    def update_product_price(
        self, db: Session, product: Product, price: int
    ) -> Product:
        """
        更新商品價格。

        :param db: Session, 資料庫會話。
        :param product: Product, 要更新的商品。
        :param price: int, 新價格。
        :return: Product, 更新後的商品。
        """
        product.price = price
        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product: Product) -> bool:
        """
        刪除商品。

        :param db: Session, 資料庫會話。
        :param product: Product, 要刪除的商品。
        :return: bool, 刪除成功返回 True。
        """
        db.delete(product)
        db.commit()
        return True

    def get_low_stock_products(self, db: Session, threshold: int = 10) -> List[Product]:
        """
        獲取庫存不足的商品。

        :param db: Session, 資料庫會話。
        :param threshold: int, 庫存警戒值。
        :return: List[Product], 庫存不足的商品列表。
        """
        return (
            db.query(Product)
            .filter(
                and_(
                    Product.stock_quantity <= threshold,
                    Product.is_service == False,
                    Product.is_active == True,
                )
            )
            .all()
        )

    def get_services_by_duration(
        self,
        db: Session,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ) -> List[Product]:
        """
        根據服務時間範圍獲取服務項目。

        :param db: Session, 資料庫會話。
        :param min_duration: Optional[int], 最小服務時間（分鐘）。
        :param max_duration: Optional[int], 最大服務時間（分鐘）。
        :return: List[Product], 符合條件的服務列表。
        """
        query = db.query(Product).filter(
            Product.is_service == True, Product.is_active == True
        )

        if min_duration is not None:
            query = query.filter(Product.duration_time >= min_duration)
        if max_duration is not None:
            query = query.filter(Product.duration_time <= max_duration)

        return query.all()


# 創建 ProductCRUD 的單例實例
product_crud = ProductCRUD()
