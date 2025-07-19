# Routers package initialization
from .users import router as users_router
from .products import router as products_router
from .schedules import router as schedules_router
from .store import router as store_router
from .appointments import router as appointments_router
from .orders import router as orders_router
from .coupons import router as coupons_router

__all__ = [
    "users_router",
    "products_router",
    "schedules_router",
    "store_router",
    "appointments_router",
    "orders_router",
    "coupons_router"
]