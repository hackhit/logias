import re

def heuristic_injection_filter(query: str) -> bool:
    """
    Analiza una consulta en busca de patrones comunes de Jailbreak, inyección de prompts
    o intentos de forzar la evasión de seguridad o cambio de rol del sistema.
    Retorna True si es sospechosa (debe ser bloqueada), False de lo contrario.
    """
    # Patrones comunes de inyección o jailbreak
    patterns = [
        r"(?i)ignore",
        r"(?i)system\s+prompt",
        r"(?i)acting\s+as\s+a",
        r"(?i)you\s+are\s+now\s+an\s+admin",
        r"(?i)como\s+un\s+administrador",
        r"(?i)ignora",
        r"(?i)ignorar",
        r"(?i)actuar\s+como",
        r"(?i)mostrar\s+la\s+clave",
        r"(?i)reveal\s+your\s+instructions",
        r"(?i)bypass\s+restrictions",
        r"(?i)sudo\s+make\s+me",
        r"(?i)sql\s+injection",
        r"(?i)drop\s+table",
        r"(?i)union\s+select"
    ]

    for pattern in patterns:
        if re.search(pattern, query):
            return True

    return False
