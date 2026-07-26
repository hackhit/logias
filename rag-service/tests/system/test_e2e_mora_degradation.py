import pytest
from litestar.testing import AsyncTestClient
from main import app

@pytest.mark.asyncio
async def test_e2e_mora_degradation_flow():
    """
    Inicia sesión como el miembro en mora (>90 días), obtiene su JWT,
    y verifica que al consultar el RAG queda degradado automáticamente a público.
    """
    async with AsyncTestClient(app=app) as ac:
        # 1. Login
        login_res = await ac.post("/auth/login", json={
            "email": "miembro.entredicho@demo.local",
            "password": "Demo2026!Mora"
        })
        assert login_res.status_code == 201 or login_res.status_code == 200
        login_data = login_res.json()
        token = login_data["access_token"]
        assert login_data["user"]["estado_membresia"] == "entredicho"

        # 2. Realizar consulta
        headers = {"Authorization": f"Bearer {token}"}
        chat_res = await ac.post("/chat/query", json={
            "query": "Quiero saber los secretos del reglamento privado"
        }, headers=headers)

        assert chat_res.status_code == 201 or chat_res.status_code == 200
        chat_data = chat_res.json()
        assert chat_data["estado_membresia"] == "entredicho"

        # Verificar que a pesar de tener rol 'miembro', está degradado y solo accede a 'publico'
        for source in chat_data["sources"]:
            assert source["nivel_acceso"] == "publico"
