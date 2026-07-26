import os
import asyncpg
from contextlib import asynccontextmanager

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "rag_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rag_secure_pass_2026")
DB_NAME = os.getenv("DB_NAME", "rag_db")

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
                    host=DB_HOST,
                    port=int(DB_PORT),
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
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
    Esto previene estrictamente la fuga de contexto entre peticiones concurrentes utilizando
    el pool de conexiones de asyncpg.
    """
    global _DB_POOL, _FORCE_MOCK_DB
    if _DB_POOL is None:
        await init_db_pool()

    async with _DB_POOL.acquire() as conn:
        if _FORCE_MOCK_DB:
            # Configurar las variables RLS para el Mock de manera segura
            role = user_role if user_role else 'publico'
            uid = user_id if user_id else ''
            await conn.execute("SET_CONFIG", "app.current_user_role", role)
            await conn.execute("SET_CONFIG", "app.current_user_id", uid)
            fecha_ref = os.getenv("FECHA_REFERENCIA_MORA", "")
            if fecha_ref:
                await conn.execute("SET_CONFIG", "app.fecha_referencia_mora", fecha_ref)
            yield conn
        else:
            # Iniciar transacción explícita
            async with conn.transaction():
                # Configurar las variables RLS para esta transacción local
                role = user_role if user_role else 'publico'
                uid = user_id if user_id else ''

                # Sanitizar y establecer las variables de sesión locales
                await conn.execute("SELECT set_config('app.current_user_role', $1, true)", role)
                await conn.execute("SELECT set_config('app.current_user_id', $2, true)", uid)

                # Si se configuró una fecha de referencia para mora, la establecemos también para la transacción
                fecha_ref = os.getenv("FECHA_REFERENCIA_MORA", "")
                if fecha_ref:
                    await conn.execute("SELECT set_config('app.fecha_referencia_mora', $1, true)", fecha_ref)

                yield conn
