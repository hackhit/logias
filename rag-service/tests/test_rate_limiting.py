import asyncio
import time
import pytest
from api.middlewares import TokenBucket

@pytest.mark.asyncio
async def test_token_bucket_rate_limiting():
    # Definir capacidad para la prueba: 3 peticiones de capacidad, recarga de 1 por segundo
    bucket = TokenBucket(capacity=3.0, refill_rate=1.0)

    # Consumir las primeras 3 de inmediato (deberían ser exitosas)
    assert await bucket.consume(1) == True
    assert await bucket.consume(1) == True
    assert await bucket.consume(1) == True

    # La cuarta petición consecutiva debería ser denegada (bucket vacío)
    assert await bucket.consume(1) == False

    # Esperar 1.1 segundos para que se recargue un token
    await asyncio.sleep(1.1)

    # Ahora debería permitir consumir un token de nuevo
    assert await bucket.consume(1) == True
    assert await bucket.consume(1) == False # Y volver a vaciarse
