# Dockerfile para la API de Litestar
FROM python:3.12-slim

# Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=astral-sh/uv:0.10.8 /uv /usr/local/bin/uv

WORKDIR /app

# Copiar configuración de dependencias
COPY pyproject.toml .

# Sincronizar / Instalar dependencias usando uv
RUN uv pip install --system -r pyproject.toml

# Copiar el código fuente
COPY . .

# Exponer el puerto de la API
EXPOSE 8000

# Comando para arrancar la app usando uvicorn (provisto por Litestar)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
