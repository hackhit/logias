import pytest
from database.connection import scoped_connection, init_db_pool, close_db_pool

@pytest.mark.asyncio
async def test_audit_table_immutability():
    """
    Intenta actualizar o eliminar registros de la tabla de auditoría,
    verificando que el trigger de inmutabilidad rechaza la operación.
    """
    await init_db_pool()

    # Insertar un registro legítimo
    async with scoped_connection(user_id="audit_system", user_role="admin") as conn:
        await conn.execute(
            "INSERT INTO auditoria (usuario_id, tipo_consulta, resultado) VALUES ($1, $2, $3)",
            "V-123", "TEST_IMMUTABILITY", "Resultado legitimo"
        )

        # Intentar un UPDATE (Debe lanzar una excepción)
        with pytest.raises(Exception) as exc_info:
            await conn.execute("UPDATE AUDITORIA SET resultado = 'Modificado' WHERE usuario_id = 'V-123';")
        assert "inmutable" in str(exc_info.value).lower()

        # Intentar un DELETE (Debe lanzar una excepción)
        with pytest.raises(Exception) as exc_info:
            await conn.execute("DELETE FROM AUDITORIA WHERE usuario_id = 'V-123';")
        assert "inmutable" in str(exc_info.value).lower()

    await close_db_pool()
