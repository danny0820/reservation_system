from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user_models import User
from app.models.product_models import Product
from app.schemas.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStatusUpdate,
    ProductStockUpdate,
    ProductPriceUpdate,
)
from app.auth import get_current_active_user, get_admin_user
from app.crud.product_crud import product_crud

router = APIRouter()


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="獲取所有商品/服務",
    description="獲取系統中所有商品和服務的列表",
)
async def get_all_products(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    is_active: Optional[bool] = Query(None, description="篩選啟用狀態"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 非管理員只能看到啟用的商品
    if current_user.role != "admin" and is_active is None:
        is_active = True

    products, total = product_crud.get_products(
        db, skip=skip, limit=limit, is_active=is_active
    )
    return products


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="創建新商品/服務",
    description="(管理員權限) 在系統中創建新的商品或服務",
)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return product_crud.create_product(db, product)


@router.get(
    "/services",
    response_model=List[ProductResponse],
    summary="獲取所有服務項目",
    description="獲取系統中所有服務項目的列表",
)
async def get_services(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    min_duration: Optional[int] = Query(None, ge=0, description="最小服務時間（分鐘）"),
    max_duration: Optional[int] = Query(None, ge=0, description="最大服務時間（分鐘）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if min_duration is not None or max_duration is not None:
        services = product_crud.get_services_by_duration(
            db, min_duration=min_duration, max_duration=max_duration
        )
    else:
        # 非管理員只能看到啟用的服務
        is_active = None if current_user.role == "admin" else True
        services = product_crud.get_products_by_type(
            db, is_service=True, skip=skip, limit=limit, is_active=is_active
        )
    return services


@router.get(
    "/products",
    response_model=List[ProductResponse],
    summary="獲取所有實體商品",
    description="獲取系統中所有實體商品的列表",
)
async def get_physical_products(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 非管理員只能看到啟用的商品
    is_active = None if current_user.role == "admin" else True
    products = product_crud.get_products_by_type(
        db, is_service=False, skip=skip, limit=limit, is_active=is_active
    )
    return products


@router.get(
    "/search",
    response_model=List[ProductResponse],
    summary="搜尋商品/服務",
    description="根據關鍵字搜尋商品或服務",
)
async def search_products(
    q: str = Query(..., min_length=1, description="搜尋關鍵字"),
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=500, description="返回的最大記錄數"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 非管理員只能搜尋啟用的商品
    is_active = None if current_user.role == "admin" else True
    products, total = product_crud.search_products(
        db, query=q, skip=skip, limit=limit, is_active=is_active
    )
    return products


@router.get(
    "/inventory/low-stock",
    response_model=List[ProductResponse],
    summary="獲取庫存不足商品",
    description="(管理員權限) 獲取庫存不足的商品列表",
)
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, description="庫存警戒值"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    products = product_crud.get_low_stock_products(db, threshold=threshold)
    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="獲取指定商品/服務",
    description="根據商品ID獲取指定商品或服務的詳細資訊",
)
async def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # 非管理員只能查看啟用的商品
    if current_user.role != "admin" and not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="更新商品/服務",
    description="(管理員權限) 根據商品ID更新指定商品或服務的資訊",
)
async def update_product_by_id(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product_crud.update_product(db, product, product_update)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除商品/服務",
    description="(管理員權限) 根據商品ID刪除指定的商品或服務",
)
async def delete_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    product_crud.delete_product(db, product)


@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse,
    summary="更新商品/服務狀態",
    description="(管理員權限) 更新指定商品或服務的啟用狀態",
)
async def update_product_status(
    product_id: str,
    status_update: ProductStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product_crud.update_product_status(db, product, status_update.is_active)


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse,
    summary="更新商品庫存",
    description="(管理員/設計師權限) 更新指定商品的庫存數量",
)
async def update_product_stock(
    product_id: str,
    stock_update: ProductStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 只有管理員和設計師可以更新庫存
    if current_user.role not in ["admin", "stylist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # 只有實體商品才有庫存概念
    if product.is_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Services do not have stock"
        )

    return product_crud.update_product_stock(db, product, stock_update.stock_quantity)


@router.patch(
    "/{product_id}/price",
    response_model=ProductResponse,
    summary="更新商品/服務價格",
    description="(管理員權限) 更新指定商品或服務的價格",
)
async def update_product_price(
    product_id: str,
    price_update: ProductPriceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product_crud.update_product_price(db, product, price_update.price)
