import os
from litestar import Litestar, get
from litestar.di import Provide
from litestar.types import Scope

from database.connection import init_db_pool, close_db_pool
from api.routers import AuthController, ChatController
from api.middlewares import RateLimitMiddleware

@get("/health")
async def health_check() -> dict:
    """
    Ruta de verificación de estado y salud del servicio.
    """
    return {"status": "healthy", "service": "rag-service-v1"}

async def check_production_warnings():
    """
    Verifica si se han habilitado variables de simulación de tiempo
    y emite una advertencia visible en los logs.
    """
    fecha_ref = os.getenv("FECHA_REFERENCIA_MORA")
    if fecha_ref:
        print("*" * 80)
        print(f"⚠️  WARNING: FECHA_REFERENCIA_MORA está activa ({fecha_ref}) — este modo NUNCA debe usarse en producción.")
        print("*" * 80)

# Cargar límites de rate limiting configurables
capacity = int(os.getenv("RATE_LIMIT_CAPACITY", "20"))
refill_rate = int(os.getenv("RATE_LIMIT_REFILL_RATE", "5"))

# Litestar espera que las factorías de middleware asíncronos o middlewares sigan una interfaz compatible.
# Para evitar problemas con la firma de lambda con kwargs, creamos una fábrica explícita.
def make_rate_limit_middleware(app):
    return RateLimitMiddleware(app, capacity=capacity, refill_rate=refill_rate)

app = Litestar(
    route_handlers=[health_check, AuthController, ChatController],
    on_startup=[init_db_pool, check_production_warnings],
    on_shutdown=[close_db_pool],
    middleware=[make_rate_limit_middleware]
)
