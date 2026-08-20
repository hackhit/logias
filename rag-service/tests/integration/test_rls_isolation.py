import asyncio
import pytest
from database.connection import scoped_connection, init_db_pool, close_db_pool

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_group().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_rls_concurrent_isolation_and_context_bleed():
    """
    Simula conexiones concurrentes de distintos usuarios al pool de conexiones
    para verificar que las transacciones y SET LOCAL de RLS aíslan el contexto
    y no hay fugas ni sangrados de roles entre peticiones concurrentes.
    """
    await init_db_pool()

    # Insertar documentos mock de varios accesos para probar aislamiento
    async with scoped_connection(user_id="ingest_admin", user_role="admin") as conn:
        await conn.execute("DELETE FROM documentos_vectoriales;")

        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_pub_int", "Contenido publico.", [0.1]*384, "publico", "doc1.pdf"
        )
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_m_int", "Contenido de miembro.", [0.1]*384, "miembro", "doc2.pdf"
        )
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_adm_int", "Contenido de administrador.", [0.1]*384, "admin", "doc3.pdf"
        )

    # Tareas concurrentes para consultar el pool usando RLS diferente
    async def query_as_public():
        async with scoped_connection(user_id=None, user_role="publico") as conn:
            # Esperar un instante para forzar concurrencia solapada
            await asyncio.sleep(0.05)
            rows = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
            return [r["nivel_acceso"] for r in rows]

    async def query_as_member():
        async with scoped_connection(user_id="V-11111111", user_role="miembro") as conn:
            await asyncio.sleep(0.02)
            rows = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
            return [r["nivel_acceso"] for r in rows]

    async def query_as_admin():
        async with scoped_connection(user_id="V-33333333", user_role="admin") as conn:
            rows = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
            return [r["nivel_acceso"] for r in rows]

    # Ejecutar concurrentemente
    res_pub, res_mem, res_adm = await asyncio.gather(
        query_as_public(),
        query_as_member(),
        query_as_admin()
    )

    # Validaciones rigurosas
    assert "publico" in res_pub and "miembro" not in res_pub and "admin" not in res_pub
    assert "miembro" in res_mem and "publico" in res_mem and "admin" not in res_mem
    assert "admin" in res_adm and "miembro" in res_adm and "publico" in res_adm

    await close_db_pool()
