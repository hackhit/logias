import pytest
from core.output_validator import validate_output

def test_output_validator_logic():
    context_chunks = [
        {"texto": "El miembro de prueba con cedula V-9876543 tiene un pago registrado por un monto de 30.00.", "documento_origen": "pagos.csv"},
        {"texto": "El reglamento establece las pautas de asistencia obligatoria.", "documento_origen": "reglamento.pdf"}
    ]

    # Caso válido: Todo contenido referenciado existe en el contexto
    assert validate_output("El miembro V-9876543 tiene un pago registrado de 30.00.", context_chunks) == True

    # Caso inválido (Alucinación de cédula): Cédula no presente en los chunks recuperados
    assert validate_output("La cedula V-11111111 esta en mora.", context_chunks) == False

    # Caso inválido (Alucinación de correo): Correo no presente
    assert validate_output("Escribe a contacto@granlogia.ve para mas informacion.", context_chunks) == False

    # Caso inválido (Alucinación de fecha): Fecha no presente
    assert validate_output("El pago se realizo en fecha 2026-05-15.", context_chunks) == False
