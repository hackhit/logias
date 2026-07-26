import pytest
import asyncio
import os

# Configurar variables globales de testing
os.environ["MOCK_LLM"] = "true"
os.environ["FORCE_MOCK_DB"] = "true"
os.environ["FECHA_REFERENCIA_MORA"] = "2026-03-01"

@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture global que provee el loop de eventos asíncronos para todas las pruebas de pytest-asyncio.
    """
    loop = asyncio.get_event_loop_group().new_event_loop()
    yield loop
    loop.close()
