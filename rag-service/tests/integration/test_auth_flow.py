import pytest
from database.connection import scoped_connection, init_db_pool, close_db_pool
from passlib.hash import argon2

@pytest.mark.asyncio
async def test_auth_login_flow():
    """
    Simula el login real consultando contraseñas cifradas en Argon2 en base de datos.
    """
    await init_db_pool()

    async with scoped_connection(user_id="auth_system", user_role="admin") as conn:
        # Intentar obtener el hash de demo para Miembro Activo
        user = await conn.fetchrow("SELECT password_hash, rol, estado_membresia FROM vista_miembros WHERE email = $1", "miembro.activo@demo.local")
        assert user is not None
        assert user["rol"] == "miembro"
        assert user["estado_membresia"] == "activo"

        # Verificar que la contraseña encriptada de demo valida de forma correcta
        is_valid = argon2.verify("Demo2026!Activo", user["password_hash"])
        assert is_valid == True

        # Una contraseña incorrecta debe fallar
        assert argon2.verify("WrongPass123", user["password_hash"]) == False

    await close_db_pool()
