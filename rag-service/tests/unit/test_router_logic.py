import pytest
from core.router import classify_intent

def test_router_logic():
    # 1. Palabras clave de pagos/mora
    assert classify_intent("¿Cómo puedo saber si estoy en mora de mis cotizaciones?") == "pagos"
    assert classify_intent("Quiero pagar mi deuda mensual de capitación") == "pagos"

    # 2. Palabras clave de reglamentos
    assert classify_intent("¿Cuáles son los artículos referentes al reglamento interno?") == "reglamentos"
    assert classify_intent("Muestra el estatuto sobre la reincorporación de miembros") == "reglamentos"

    # 3. Consultas generales (debe realizar fallback seguro a 'general')
    assert classify_intent("¿Dónde queda la logia Sol de Oriente?") == "general"
    assert classify_intent("Háblame de los grandes maestros de la masonería en Venezuela") == "general"
