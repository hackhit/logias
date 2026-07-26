import os
import logging
from litestar import Litestar, get
from litestar.di import Provide
from litestar.types import Scope

from core.settings import settings
from database.connection import init_db_pool, close_db_pool
from api.routers import AuthController, ChatController
from api.middlewares import RateLimitMiddleware

# Configurar logger
logger = logging.getLogger("rag-service")

@get("/health")
async def health_check() -> dict:
    """
    Ruta de verificación de estado y salud del servicio.
    """
    return {"status": "healthy", "service": "rag-service-v1"}

async def check_production_warnings():
    """
    Verifica si se han habilitado variables de simulación de tiempo
    y emite una advertencia visible de nivel WARNING en los logs de producción (Prioridad 1.2).
    """
    fecha_ref = settings.FECHA_REFERENCIA_MORA
    if fecha_ref:
        logger.warning(
            "⚠️  WARNING: FECHA_REFERENCIA_MORA está activa (%s) — este modo NUNCA debe usarse en producción.",
            fecha_ref
        )
        print("*" * 80)
        print(f"⚠️  WARNING: FECHA_REFERENCIA_MORA está activa ({fecha_ref}) — este modo NUNCA debe usarse en producción.")
        print("*" * 80)

def make_rate_limit_middleware(app):
    return RateLimitMiddleware(app, capacity=settings.RATE_LIMIT_CAPACITY, refill_rate=settings.RATE_LIMIT_REFILL_RATE)

app = Litestar(
    route_handlers=[health_check, AuthController, ChatController],
    on_startup=[init_db_pool, check_production_warnings],
    on_shutdown=[close_db_pool],
    middleware=[make_rate_limit_middleware]
)
