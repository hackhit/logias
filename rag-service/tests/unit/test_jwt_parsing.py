import pytest
from jose import jwt
from api.auth import create_access_token, decode_access_token, JWT_SECRET, ALGORITHM

def test_jwt_validation_and_parsing():
    payload = {"sub": "V-123456", "rol": "miembro", "email": "test@demo.local"}

    # 1. Crear y decodificar token válido
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "V-123456"
    assert decoded["rol"] == "miembro"

    # 2. Firma inválida
    bad_token = token + "corrupt"
    assert decode_access_token(bad_token) is None

    # 3. Payload inconsistente o vacío
    assert decode_access_token("not_a_jwt_at_all") is None
