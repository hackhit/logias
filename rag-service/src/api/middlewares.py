import time
import asyncio
from litestar.middleware import AbstractMiddleware
from litestar.datastructures import State
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_429_TOO_MANY_REQUESTS
from litestar.types import ASGIApp, Receive, Scope, Send

class TokenBucket:
    """
    Algoritmo de Token Bucket para control de flujos y Rate Limiting.
    """
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now

            # Recargar tokens según la tasa
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class RateLimitMiddleware(AbstractMiddleware):
    """
    Middleware de Rate Limiting para Litestar que implementa Token Bucket.
    Almacena los buckets por dirección IP del cliente de forma thread-safe/asyncio-safe.
    """
    def __init__(self, app: ASGIApp, capacity: int, refill_rate: int):
        super().__init__(app)
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}
        self.lock = asyncio.Lock()

    async def get_bucket(self, ip: str) -> TokenBucket:
        async with self.lock:
            if ip not in self.buckets:
                self.buckets[ip] = TokenBucket(self.capacity, self.refill_rate)
            return self.buckets[ip]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Solo aplicar rate limiting a endpoints de /chat o /auth
        path = scope.get("path", "")
        if path.startswith("/chat") or path.startswith("/auth"):
            # Obtener IP del cliente
            client = scope.get("client")
            ip = client[0] if client else "127.0.0.1"

            bucket = await self.get_bucket(ip)
            allowed = await bucket.consume(1)

            if not allowed:
                # Retornar error HTTP 429 de forma controlada sin bloquear el loop de eventos
                raise HTTPException(
                    detail="Demasiadas peticiones concurrentes. Límite de tasa excedido.",
                    status_code=HTTP_429_TOO_MANY_REQUESTS
                )

        await self.app(scope, receive, send)


async def log_audit_to_db(user_id: str | None, tipo_consulta: str, resultado: str):
    """
    Módulo de auditoría con AWAIT EXPLÍCITO (no fire-and-forget) para persistir
    cada interacción de seguridad en la tabla inmutable.
    """
    from database.connection import scoped_connection
    # Siempre ejecutamos el log de auditoría bajo el rol de administrador para asegurar la escritura
    # o como superusuario de base de datos
    async with scoped_connection(user_id="audit_system", user_role="admin") as conn:
        try:
            await conn.execute(
                """
                INSERT INTO auditoria (usuario_id, tipo_consulta, resultado)
                VALUES ($1, $2, $3);
                """,
                user_id if user_id else "anonimo",
                tipo_consulta,
                resultado
            )
        except Exception as e:
            print(f"Error crítico guardando auditoría: {e}")
