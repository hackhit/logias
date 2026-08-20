from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

JWT_SECRET = os.getenv("JWT_SECRET", "super_secure_rag_jwt_secret_key_2026_long_and_complex_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    """
    Crea un token JWT de acceso para un usuario autenticado.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """
    Decodifica y valida un token JWT, retornando los datos del usuario si es válido.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
