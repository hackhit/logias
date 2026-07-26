import os
import sys

# Configuración y validación estricta de variables de entorno de producción
class Settings:
    def __init__(self):
        # Campos de base de datos obligatorios sin valores por defecto en producción
        # Para que falle rápido y explícito si falta configuración secreta
        try:
            self.DB_PASSWORD = os.environ["DB_PASSWORD"]
        except KeyError:
            print("ERROR CRÍTICO: La variable de entorno 'DB_PASSWORD' es requerida.", file=sys.stderr)
            sys.exit(1)

        try:
            self.JWT_SECRET = os.environ["JWT_SECRET"]
        except KeyError:
            print("ERROR CRÍTICO: La variable de entorno 'JWT_SECRET' es requerida.", file=sys.stderr)
            sys.exit(1)

        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_USER = os.getenv("DB_USER", "rag_user")
        self.DB_NAME = os.getenv("DB_NAME", "rag_db")

        self.MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"
        self.FECHA_REFERENCIA_MORA = os.getenv("FECHA_REFERENCIA_MORA", "")
        self.MODEL_PATH = os.getenv("MODEL_PATH", "")

        self.RATE_LIMIT_CAPACITY = int(os.getenv("RATE_LIMIT_CAPACITY", "20"))
        self.RATE_LIMIT_REFILL_RATE = int(os.getenv("RATE_LIMIT_REFILL_RATE", "5"))

# Instancia global única de settings
settings = Settings()
