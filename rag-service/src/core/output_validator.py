import re

def validate_output(generated_text: str, context_chunks: list[dict]) -> bool:
    """
    Validador de salida determinista (Heurístico):
    Verifica mecánicamente que las entidades/datos mencionados en el texto generado
    están presentes en los chunks de contexto recuperados del scope autorizado.
    Si se detecta una mención que no proviene del contexto autorizado (ej. alucinaciones),
    esta función retorna False, permitiendo al sistema descartar la respuesta y usar un fallback seguro.
    """
    if not generated_text:
        return False

    # Extraer entidades numéricas o palabras clave importantes del texto generado
    # Ej. números de cédula, montos específicos, fechas, correos electrónicos, etc.
    # Estas son las entidades más críticas sujetas a alucinación.

    # 1. Buscar cédulas (formato V-XXXXXXX o números largos)
    cedulas_in_text = re.findall(r"\bV-\d{6,9}\b", generated_text)

    # 2. Buscar correos electrónicos
    emails_in_text = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", generated_text)

    # 3. Buscar fechas en formato YYYY-MM-DD
    dates_in_text = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", generated_text)

    # Unir todo el texto del contexto recuperado para la verificación
    context_text = " ".join([chunk.get("texto", "") for chunk in context_chunks]).lower()

    # Validar cédulas
    for cedula in cedulas_in_text:
        if cedula.lower() not in context_text:
            print(f"VALIDADOR DE SALIDA: Detectada cédula alucinada/no autorizada: {cedula}")
            return False

    # Validar correos
    for email in emails_in_text:
        if email.lower() not in context_text:
            print(f"VALIDADOR DE SALIDA: Detectado correo alucinado/no autorizada: {email}")
            return False

    # Validar fechas
    for dt in dates_in_text:
        if dt.lower() not in context_text:
            print(f"VALIDADOR DE SALIDA: Detectada fecha alucinada/no autorizada: {dt}")
            return False

    return True
