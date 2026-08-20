import pytest
from litestar.testing import AsyncTestClient
from main import app

@pytest.mark.asyncio
async def test_e2e_public_query():
    """
    Simula una consulta pública desde el cliente HTTP de la API,
    verificando que solo se citan fragmentos de nivel público y se responde correctamente.
    """
    async with AsyncTestClient(app=app) as ac:
        response = await ac.post("/chat/query", json={"query": "Hola, ¿cuál es el comunicado oficial?"})
        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data

        # Un usuario público no tiene estado_membresia en la respuesta
        assert data["estado_membresia"] is None

        # Validar que los orígenes/chunks recuperados son únicamente de nivel público
        for source in data["sources"]:
            assert source["nivel_acceso"] == "publico"
