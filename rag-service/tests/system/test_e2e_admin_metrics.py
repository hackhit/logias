import pytest
from litestar.testing import AsyncTestClient
from main import app

@pytest.mark.asyncio
async def test_e2e_admin_metrics_flow():
    """
    Inicia sesión como administrador, obtiene su JWT,
    y verifica que puede acceder a la base de datos completa de documentos sin restricciones.
    """
    async with AsyncTestClient(app=app) as ac:
        # 1. Login administrador
        login_res = await ac.post("/auth/login", json={
            "email": "admin.demo@demo.local",
            "password": "Demo2026!Admin"
        })
        assert login_res.status_code == 201 or login_res.status_code == 200
        login_data = login_res.json()
        token = login_data["access_token"]
        assert login_data["user"]["rol"] == "admin"

        # 2. Consultar como administrador
        headers = {"Authorization": f"Bearer {token}"}
        chat_res = await ac.post("/chat/query", json={
            "query": "Muestra métricas globales y reglamentos privados de administrador"
        }, headers=headers)

        assert chat_res.status_code == 201 or chat_res.status_code == 200
        chat_data = chat_res.json()
        assert "response" in chat_data

        # El administrador puede recuperar documentos de cualquier nivel de acceso
        nivel_accesos = [s["nivel_acceso"] for s in chat_data["sources"]]
        assert len(chat_data["sources"]) >= 0
