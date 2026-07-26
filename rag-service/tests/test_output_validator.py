import pytest
from core.output_validator import validate_output

def test_output_validator():
    # Contexto autorizado de prueba
    context_chunks = [
        {"texto": "El reglamento de la Gran Logia fue firmado por el Gran Maestro el 2026-01-15.", "documento_origen": "reglamento.pdf"},
        {"texto": "El miembro de prueba con cedula V-12345678 esta al dia.", "documento_origen": "miembros.csv"}
    ]

    # Caso 1: Salida válida con datos presentes en el contexto
    valid_text = "Segun el reglamento firmado el 2026-01-15, el miembro V-12345678 esta al dia."
    assert validate_output(valid_text, context_chunks) == True

    # Caso 2: Salida con alucinación de cédula (no presente en el contexto)
    invalid_cedula = "El miembro con cedula V-99999999 esta al dia."
    assert validate_output(invalid_cedula, context_chunks) == False

    # Caso 3: Salida con alucinación de fecha (no presente en el contexto)
    invalid_date = "El reglamento fue modificado el 2026-12-25."
    assert validate_output(invalid_date, context_chunks) == False

    # Caso 4: Salida con correo alucinado
    invalid_email = "Escribe a admin@logias.local para mas info."
    assert validate_output(invalid_email, context_chunks) == False
