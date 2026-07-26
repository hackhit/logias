import os
import pytest
import asyncio
from datetime import datetime

# Configuramos variables de entorno para pruebas
os.environ["MOCK_LLM"] = "true"
os.environ["FECHA_REFERENCIA_MORA"] = "2026-03-01"

from etl.synthetic_data import generate_synthetic_data
from etl.tabular_ingestor import ingest_tabular_data
from database.connection import scoped_connection, init_db_pool, close_db_pool

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_group().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_mora_and_rls_isolation():
    # Inicializar pool de base de datos
    await init_db_pool()

    # 1. Probar Regla de Negocio: Mora de Pagos > 90 días
    # Obtener el estado del miembro activo demo en la vista recalculada
    async with scoped_connection(user_id="audit_system", user_role="admin") as conn:
        # Verificar miembro activo
        activo = await conn.fetchrow("SELECT estado_membresia FROM vista_miembros WHERE email = $1", "miembro.activo@demo.local")
        assert activo is not None
        assert activo["estado_membresia"] == "activo", f"Se esperaba 'activo', se obtuvo: {activo['estado_membresia']}"

        # Verificar miembro en mora (último pago: 2025-10-15; ref: 2026-03-01 -> 137 días de diferencia)
        mora = await conn.fetchrow("SELECT estado_membresia FROM vista_miembros WHERE email = $1", "miembro.entredicho@demo.local")
        assert mora is not None
        assert mora["estado_membresia"] == "entredicho", f"Se esperaba 'entredicho' por mora de >90 días, se obtuvo: {mora['estado_membresia']}"

    # 2. Probar Row-Level Security (RLS) en documentos_vectoriales
    # Primero insertamos algunos documentos de prueba
    async with scoped_connection(user_id="ingest_system", user_role="admin") as conn:
        await conn.execute("DELETE FROM documentos_vectoriales;")

        # Insertar documento público
        await conn.execute(
            """
            INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING;
            """,
            "hash_pub_1", "Contenido publico de prueba.", [0.1]*384, "publico", "doc_pub.pdf"
        )
        # Insertar documento de miembro
        await conn.execute(
            """
            INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING;
            """,
            "hash_m_1", "Contenido privado de miembro de prueba.", [0.1]*384, "miembro", "doc_miembro.pdf"
        )
        # Insertar documento de administrador
        await conn.execute(
            """
            INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING;
            """,
            "hash_adm_1", "Contenido secreto de administrador de prueba.", [0.1]*384, "admin", "doc_admin.pdf"
        )

    # Caso A: Un usuario público (anónimo) solo recupera contenido de nivel público
    async with scoped_connection(user_id=None, user_role="publico") as conn:
        docs = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
        assert len(docs) == 1
        assert docs[0]["nivel_acceso"] == "publico"

    # Caso B: Un miembro ACTIVO puede ver contenido público + miembro
    async with scoped_connection(user_id="V-11111111", user_role="miembro") as conn:
        docs = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales ORDER BY nivel_acceso DESC;")
        assert len(docs) == 2
        niveles = [d["nivel_acceso"] for d in docs]
        assert "publico" in niveles
        assert "miembro" in niveles
        assert "admin" not in niveles

    # Caso C: Un miembro en MORA (entredicho) queda degradado y solo ve contenido público
    async with scoped_connection(user_id="V-22222222", user_role="miembro") as conn:
        docs = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
        assert len(docs) == 1
        assert docs[0]["nivel_acceso"] == "publico"

    # Caso D: Un administrador puede ver todo el corpus de documentos
    async with scoped_connection(user_id="V-33333333", user_role="admin") as conn:
        docs = await conn.fetch("SELECT texto, nivel_acceso FROM documentos_vectoriales;")
        assert len(docs) == 3

    await close_db_pool()
