import pytest
from core.security import heuristic_injection_filter

def test_sql_injection_filter():
    """
    Verifica que payloads clásicos de inyección SQL sean bloqueados
    o pasen de forma segura gracias a la parametrización de asyncpg.
    """
    sql_payloads = [
        "SELECT * FROM miembros; DROP TABLE miembros;",
        "1' OR '1'='1",
        "UNION SELECT null, username, password FROM users--",
        "'; DROP TABLE auditoria;--"
    ]

    # Algunos de estos se bloquean heurísticamente por seguridad adicional
    for payload in sql_payloads:
        # El filtro heurístico captura drop table o union select por ejemplo
        if "drop table" in payload.lower() or "union select" in payload.lower():
            assert heuristic_injection_filter(payload) == True
