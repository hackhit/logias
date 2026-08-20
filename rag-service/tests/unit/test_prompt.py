import pytest
from core.prompt import assemble_prompt

def test_prompt_assembly():
    query = "¿Cómo puedo ver mi historial de pagos?"
    context_chunks = [
        {"texto": "El miembro de prueba con cedula V-9876543 tiene un pago registrado por un monto de 30.00.", "documento_origen": "pagos.csv"},
        {"texto": "El reglamento establece las pautas de asistencia obligatoria.", "documento_origen": "reglamento.pdf"}
    ]

    prompt = assemble_prompt(query, context_chunks)
    assert query in prompt
    assert "pagos.csv" in prompt
    assert "reglamento.pdf" in prompt
    assert "V-9876543" in prompt
