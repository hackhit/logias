import pytest
import json
import os
from litestar.testing import AsyncTestClient
from main import app
from database.connection import scoped_connection, init_db_pool

@pytest.mark.asyncio
async def test_regression_suite_against_baseline():
    """
    Lee las preguntas de referencia del baseline_responses.json
    y realiza consultas en modo MOCK_LLM=true, asegurando que las respuestas
    obtenidas no sufren regresiones inesperadas en su formato ni coherencia de contenido.
    """
    await init_db_pool()

    # Poblar corpus para regresión
    async with scoped_connection(user_id="V-33333333", user_role="admin") as conn:
        await conn.execute("DELETE FROM documentos_vectoriales;")
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_reg_1", "Este es un comunicado oficial público.", [0.1]*384, "publico", "doc1.pdf"
        )
        await conn.execute(
            "INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen) "
            "VALUES ($1, $2, $3, $4, $5)",
            "hash_reg_2", "El reglamento establece las pautas sobre asistencia obligatoria.", [0.1]*384, "miembro", "doc2.pdf"
        )

    baseline_path = os.path.join(os.path.dirname(__file__), "baseline_responses.json")
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline_cases = json.load(f)

    async with AsyncTestClient(app=app) as ac:
        for case in baseline_cases:
            # Login para obtener token si no es público
            headers = {}
            if case["role"] != "publico":
                email = f"{case['role']}.demo@demo.local" if case["role"] == "admin" else "miembro.activo@demo.local"
                pwd = "Demo2026!Admin" if case["role"] == "admin" else "Demo2026!Activo"

                login_res = await ac.post("/auth/login", json={
                    "email": email,
                    "password": pwd
                })
                assert login_res.status_code in (200, 201)
                token = login_res.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

            # Hacer consulta
            chat_res = await ac.post("/chat/query", json={"query": case["query"]}, headers=headers)
            assert chat_res.status_code in (200, 201)
            chat_data = chat_res.json()

            # Verificar que la respuesta contiene las fuentes o palabras esperadas del baseline
            response_text = chat_data["response"].lower()
            assert case["expected_text"].lower() in response_text, f"Fallo de regresión en consulta {case['id']}"
