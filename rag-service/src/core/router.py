import re

"""
DISEÑO DE DOS CAPAS DEL ENRUTADOR DETERMINISTA (Mencionada en Addendum del cliente):

1. CAPA DE SEGURIDAD (OBLIGATORIA, NO NEGOCIABLE):
   El scope real de la búsqueda vectorial (qué tablas o documentos son alcanzables)
   lo determina UNICAMENTE el rol máximo del JWT y las políticas RLS de PostgreSQL.
   - Público: consulta nivel_acceso = 'publico'.
   - Miembro (activo): consulta 'publico' y 'miembro'.
   - Miembro (en entredicho por mora > 90 días): consulta 'publico' solamente (degradado automáticamente por mora).
   - Administrador: consulta todo ('publico', 'miembro', 'admin').
   Esta capa es gestionada estrictamente en la base de datos a nivel transaccional y RLS,
   lo cual nunca depende del contenido textual de la pregunta ni del clasificador de intenciones.

2. CAPA DE INTENCIÓN (OPTIMIZACIÓN, NO SEGURIDAD):
   Un filtro de palabras clave (ej. "reglamento", "pago", "mora", "estatuto") que, dentro del scope ya autorizado,
   prioriza qué subconjunto de documentos buscar primero para mejorar la relevancia y la velocidad.
   - Si el clasificador heurístico de intención falla, se realiza un fallback automático para buscar
     en todo el scope autorizado de forma habitual, garantizando que NUNCA se produzca una fuga de datos.
"""

def classify_intent(query: str) -> str:
    """
    Capa de Intención: Determina la intención heurística para optimizar la relevancia de búsqueda
    dentro del scope ya autorizado de RLS.
    """
    query_lower = query.lower()

    # Palabras clave relacionadas con reglamentos internos
    reglamentos_keywords = ["reglamento", "estatuto", "normativa", "deber", "derecho", "capítulo", "artículo", "reincorporación"]
    # Palabras clave relacionadas con pagos o mora
    pagos_keywords = ["pago", "mora", "cuota", "cotización", "deuda", "tesorero", "capitación", "entredicho", "activo", "financiero"]

    # Verificar coincidencias
    if any(kw in query_lower for kw in pagos_keywords):
        return "pagos"
    elif any(kw in query_lower for kw in reglamentos_keywords):
        return "reglamentos"

    return "general"
