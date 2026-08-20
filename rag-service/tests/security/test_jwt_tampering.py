import pytest
from jose import jwt
from api.auth import decode_access_token, create_access_token

def test_jwt_tampering_attempts():
    """
    Simula intentos de falsificación o alteración de tokens JWT.
    """
    valid_payload = {"sub": "V-11111111", "rol": "miembro", "email": "user@demo.local"}
    token = create_access_token(valid_payload)

    # 1. Modificar el rol a 'admin' sin volver a firmar (JWT corrupto)
    tampered_parts = token.split(".")
    # Si alteramos la sección central, el decodificador de jose debe fallar al verificar la firma
    tampered_token = tampered_parts[0] + "." + tampered_parts[1] + "wrong" + "." + tampered_parts[2]
    assert decode_access_token(tampered_token) is None

    # 2. Token vacío o de firma incorrecta
    assert decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature") is None
