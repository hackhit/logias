import os
import asyncpg
from contextlib import asynccontextmanager
from core.settings import settings

# Pool de conexiones global
_DB_POOL = None

# Variable para forzar simulación de base de datos si Postgres no está disponible (ej. entornos CI / Sandbox limitados)
_FORCE_MOCK_DB = os.getenv("FORCE_MOCK_DB", "false").lower() == "true"

async def init_db_pool():
    global _DB_POOL, _FORCE_MOCK_DB
    if _DB_POOL is None:
        if _FORCE_MOCK_DB:
            from database.mock_connection import MockPool
            _DB_POOL = MockPool()
            print("INFO: Cargando Mock de Conexión de base de datos simulado (FORCE_MOCK_DB=true).")
        else:
            try:
                _DB_POOL = await asyncpg.create_pool(
                    host=settings.DB_HOST,
                    port=int(settings.DB_PORT),
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    database=settings.DB_NAME,
                    min_size=5,
                    max_size=20,
                    timeout=5.0
                )
                print("Pool de conexiones de PostgreSQL inicializado correctamente.")
            except Exception as e:
                print(f"Advertencia: No se pudo conectar a PostgreSQL ({e}). Cargando Mock de Base de Datos para asegurar resiliencia en pruebas y entornos sin Postgres local.")
                from database.mock_connection import MockPool
                _DB_POOL = MockPool()
                _FORCE_MOCK_DB = True

async def close_db_pool():
    global _DB_POOL
    if _DB_POOL is not None:
        await _DB_POOL.close()
        print("Pool de conexiones de PostgreSQL cerrado correctamente.")

@asynccontextmanager
async def scoped_connection(user_id=None, user_role=None):
    """
    Gestor de contexto asíncrono que obtiene una conexión del pool y realiza de forma segura
    un SET LOCAL de la identidad y rol del usuario dentro de una transacción explícita por petición.
    Previene estrictamente la fuga de contexto entre peticiones concurrentes utilizando
    el pool de conexiones de asyncpg.
    """
    global _DB_POOL, _FORCE_MOCK_DB
    if _DB_POOL is None:
        await init_db_pool()

    async with _DB_POOL.acquire() as conn:
        role = user_role if user_role else 'publico'
        uid = user_id if user_id else ''
        fecha_ref = settings.FECHA_REFERENCIA_MORA

        if _FORCE_MOCK_DB:
            # Seteamos las variables en el Mock de manera identica
            await conn.execute(
                "SELECT set_config('app.current_user_role', $1, true), set_config('app.current_user_id', $2, true)",
                role, uid
            )
            if fecha_ref:
                await conn.execute("SELECT set_config('app.fecha_referencia_mora', $1, true)", fecha_ref)
            yield conn
        else:
            # Iniciar transacción explícita
            async with conn.transaction():
                # Corrección prioritaria 0.1 de parámetros de set_config en transacción explícita
                await conn.execute(
                    "SELECT set_config('app.current_user_role', $1, true), set_config('app.current_user_id', $2, true)",
                    role, uid
                )

                if fecha_ref:
                    await conn.execute("SELECT set_config('app.fecha_referencia_mora', $1, true)", fecha_ref)

                yield conn
