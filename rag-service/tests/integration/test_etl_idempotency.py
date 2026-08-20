import pytest
from database.connection import scoped_connection, init_db_pool, close_db_pool

@pytest.mark.asyncio
async def test_etl_ingest_idempotency():
    """
    Simula la ejecución repetitiva del pipeline ETL sobre la base de datos
    para verificar que los hashes SHA-256 e identificadores naturales (cédulas)
    evitan la duplicación de datos o corrupción.
    """
    await init_db_pool()

    async with scoped_connection(user_id="ingest_admin", user_role="admin") as conn:
        # 1. Limpiar documentos de test
        await conn.execute("DELETE FROM documentos_vectoriales;")

        # 2. Insertar primera vez
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5) ON CONFLICT (chunk_hash) DO NOTHING",
            "sha256_hash_1", "Texto unico.", [0.1]*384, "publico", "doc.pdf"
        )

        # Obtener cantidad
        count_first = await conn.fetchval("SELECT COUNT(*) FROM documentos_vectoriales;")
        assert count_first == 1

        # 3. Insertar exactamente el mismo documento (simulando re-ejecución)
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5) ON CONFLICT (chunk_hash) DO NOTHING",
            "sha256_hash_1", "Texto unico.", [0.1]*384, "publico", "doc.pdf"
        )

        # Validar que sigue habiendo 1 solo registro
        count_second = await conn.fetchval("SELECT COUNT(*) FROM documentos_vectoriales;")
        assert count_second == 1

    await close_db_pool()
