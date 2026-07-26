import pytest
from litestar.testing import AsyncTestClient
from main import app
from database.connection import scoped_connection, init_db_pool

@pytest.mark.asyncio
async def test_e2e_member_query_flow():
    """
    Realiza el flujo de login de un miembro activo, obtiene su JWT,
    y realiza una consulta privada RAG verificando que puede leer el reglamento.
    """
    await init_db_pool()

    # Asegurar que existan documentos en la base de datos de test
    async with scoped_connection(user_id="V-33333333", user_role="admin") as conn:
        await conn.execute("DELETE FROM documentos_vectoriales;")
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_member_test_e2e", "El reglamento establece las pautas sobre asistencia obligatoria.", [0.1]*384, "miembro", "reglamento.pdf"
        )

    async with AsyncTestClient(app=app) as ac:
        # 1. Login real
        login_res = await ac.post("/auth/login", json={
            "email": "miembro.activo@demo.local",
            "password": "Demo2026!Activo"
        })
        assert login_res.status_code == 201 or login_res.status_code == 200
        login_data = login_res.json()
        token = login_data["access_token"]

        # 2. Consulta RAG con JWT
        headers = {"Authorization": f"Bearer {token}"}
        chat_res = await ac.post("/chat/query", json={
            "query": "Quiero saber las pautas sobre asistencia obligatoria"
        }, headers=headers)

        assert chat_res.status_code == 201 or chat_res.status_code == 200
        chat_data = chat_res.json()
        assert "response" in chat_data
        assert chat_data["estado_membresia"] == "activo"

        # Verificar que el miembro activo puede acceder a fuentes de nivel miembro
        nivel_accesos = [s["nivel_acceso"] for s in chat_data["sources"]]
        assert "miembro" in nivel_accesos
