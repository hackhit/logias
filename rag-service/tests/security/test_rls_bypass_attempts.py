import pytest
from database.connection import scoped_connection, init_db_pool, close_db_pool

@pytest.mark.asyncio
async def test_rls_bypass_attempts():
    """
    Intenta saltarse la RLS forzando consultas con parámetros alterados.
    Las políticas de RLS garantizan que la variable de sesión 'app.current_user_role'
    limita la búsqueda independientemente del texto de la consulta.
    """
    await init_db_pool()

    # 1. Intentar ver documentos de miembro como 'publico' (debe dar 0 documentos de miembro)
    async with scoped_connection(user_id=None, user_role="publico") as conn:
        docs = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales WHERE nivel_acceso = 'miembro';")
        # El RLS filtra de forma automática
        for doc in docs:
            assert doc["nivel_acceso"] == "publico"

    await close_db_pool()
