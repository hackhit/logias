# 🏛️ Microservicio RAG Privado de Punta a Punta

Este directorio contiene la implementación completa de la propuesta técnica para el **Microservicio RAG Conversacional 100% On-Premise**, desarrollado como una extensión segura del catálogo de la Gran Logia de la República de Venezuela.

Todo el desarrollo de esta característica vive de forma aislada en la rama `feature/rag-privado-v1` y bajo este directorio `rag-service/`, cumpliendo estrictamente con la **restricción no negociable** de no modificar ni alterar el código de la rama `main` en producción.

---

## ⚠️ Rotación de secretos post-remediación

Tras la auditoría de seguridad y de acuerdo con el hallazgo de GitGuardian, se han **eliminado de forma estricta todos los valores por defecto o contraseñas hardcodeadas en el código fuente de la aplicación** (como `DB_PASSWORD` o `JWT_SECRET`).

Cualquier contraseña o clave que haya coincidido con los placeholders originales en los primeros commits del desarrollo **debe considerarse totalmente comprometida y rotarse obligatoriamente** antes de realizar el despliegue en entornos de producción reales. El microservicio ahora valida que todos los secretos estén presentes en el entorno en su arranque y fallará con un mensaje claro si alguno no está configurado.

---

## 🚀 Arquitectura y Decisiones de Seguridad

El diseño del microservicio se basa en la robustez, el control estricto de acceso a los datos y la inmutabilidad de la auditoría:

1. **Aislamiento de Datos por Row-Level Security (RLS) de PostgreSQL**:
   - Esta es la frontera real de seguridad. Las consultas de vectores y datos privados se aíslan utilizando RLS.
   - En cada petición, dentro de una transacción explícita, se ejecuta `SET LOCAL` para establecer el rol (`app.current_user_role`) y la cédula del usuario (`app.current_user_id`). Esto evita cualquier riesgo de fuga de contexto en conexiones concurrentes del pool de `asyncpg`.
   - Se ha implementado `FORCE ROW LEVEL SECURITY` obligatoriamente en todas las tablas para garantizar que incluso el rol owner esté sujeto a las políticas de seguridad.
   - Se ha diseñado una **separación real de roles de base de datos** (Prioridad 0.2): el rol `app_runtime` es el utilizado en ejecución de la app (no es propietario de ninguna tabla), limitando sus privilegios estrictamente mediante GRANTs.
   - Se implementa una jerarquía real de roles:
     - `publico` < `miembro` < `admin`.

2. **Cálculo Determinista de Mora (Regla de los 3 meses / 90 días)**:
   - El estado de membresía **nunca es responsabilidad de la IA ni de un prompt**. Se calcula de forma matemática y determinista en la base de datos a nivel de vista/función (marcada como `STABLE` para máximo rendimiento):
     - `CURRENT_DATE - fecha_ultimo_pago > 90` -> `estado_membresia = 'entredicho'`.
   - Si un miembro se encuentra en estado `entredicho`, queda degradado automáticamente al nivel de acceso `publico` y pierde todo el acceso a secciones privadas/documentos de nivel `miembro`.
   - **Parámetro de Referencia para Demos**: Soporta la variable de entorno `FECHA_REFERENCIA_MORA` (formato `YYYY-MM-DD`). Si está activa, se utiliza para simular consistencia con fechas fijas del dataset sintético. Genera un Warning visible en los logs advirtiendo que no debe utilizarse en producción.

3. **Enrutador Determinista de Contexto (Dos Capas)**:
   - **Capa 1: Seguridad (Obligatoria)**: El scope máximo de documentos alcanzables es decidido estrictamente por el rol del JWT y RLS de base de datos.
   - **Capa 2: Intención (Optimización)**: Un clasificador heurístico rápido en Python que detecta palabras clave (ej: "reglamento", "pago") para priorizar colecciones dentro del scope ya autorizado, optimizando la relevancia y velocidad sin poner en riesgo la seguridad.

4. **Validador de Salida Determinista contra Alucinaciones**:
   - Mecanismo en Python que verifica mecánicamente que las entidades críticas mencionadas en el texto generado (cédulas, correos, fechas) existan explícitamente en los fragmentos de contexto recuperados. Si detecta una entidad alucinada, descarta la respuesta y devuelve un fallback seguro.

5. **Auditoría Inmutable**:
   - Tabla `auditoria` con un trigger PostgreSQL que bloquea cualquier sentencia `UPDATE` o `DELETE`, permitiendo exclusivamente escrituras (`INSERT`), asegurando el cumplimiento de la trazabilidad.

6. **Inferencia Local y Cola Secuencial**:
   - Utiliza `llama-cpp-python` para cargar un modelo GGUF de 4 bits una sola vez en memoria.
   - Todas las llamadas al modelo pasan por un worker asíncrono con una cola secuencial (`asyncio.Queue`) de un solo consumidor, previniendo la saturación del procesador. Las llamadas pesadas corren dentro de un `run_in_executor` thread pool.
   - **Modo Mock Determinista**: Se puede activar `MOCK_LLM=true` en entornos CI o de recursos limitados. Este modo no simula creatividad sino que extrae un resumen predecible y reproducible de las fuentes recuperadas, garantizando pruebas automatizadas 100% estables.

---

## 🛠️ Estructura del Proyecto

```
rag-service/
├── Dockerfile                  # Dockerfile para la API de Litestar
├── Dockerfile.streamlit        # Dockerfile para la demo interactiva
├── docker-compose.yml          # Coordinación de los servicios (Nginx, Postgres, Litestar, Streamlit)
├── .env.example                # Variables de entorno de referencia
├── README.md                   # Esta documentación
├── infra/
│   ├── nginx/
│   │   └── nginx.conf          # Proxy inverso Nginx con enrutamiento seguro
│   └── postgres/
│       ├── init.sql            # Esquema de base de datos, pgvector, RLS, triggers y mora
│       └── postgresql.conf     # Parámetros optimizados de PostgreSQL
├── src/
│   ├── main.py                 # Punto de entrada de la API Litestar
│   ├── pyproject.toml          # Dependencias y metadatos con gestor 'uv'
│   ├── api/
│   │   ├── auth.py             # Autenticación JWT y login
│   │   ├── middlewares.py      # Rate limiter Token Bucket + Auditoría con await explícito
│   │   └── routers.py          # Endpoints REST de autenticación y RAG
│   ├── core/
│   │   ├── settings.py         # Centralización de lectura y validación de variables de entorno (Prioridad 1.1)
│   │   ├── security.py         # Filtro heurístico anti-inyecciones
│   │   ├── router.py           # Enrutador determinista de dos capas (Seguridad + Intención)
│   │   ├── output_validator.py # Validador determinista de salida contra alucinaciones
│   │   └── prompt.py           # Ensamblaje de prompts contextuales
│   ├── database/
│   │   ├── connection.py       # Pool asyncpg con transacciones scoped_connection (RLS)
│   │   └── mock_connection.py  # Mock resiliente de base de datos para entornos CI/Sandbox
│   ├── ai_engine/
│   │   ├── engine_interface.py # Interfaz abstracta del motor de IA
│   │   ├── llm.py              # Inferencia Llama-cpp + Cola secuencial + Modo Mock
│   │   └── embeddings.py       # Embeddings locales de 384 dimensiones
│   └── etl/
│       ├── chunker.py          # Chunking semántico jerárquico por capítulo/artículo
│       ├── pdf_ingestor.py     # Ingestor idempotente de documentos PDF con pdfplumber
│       ├── synthetic_data.py   # Generador de dataset sintético de 550 miembros
│       └── tabular_ingestor.py # Ingestor idempotente de CSV/Excel con Polars lazy
├── tests/                      # Suite de tests automatizados
│   ├── conftest.py             # Fixture global asíncrona de sesión
│   ├── unit/                   # Tests unitarios puros rápidos
│   ├── integration/            # Tests de integración contra BD PostgreSQL/Mock
│   ├── security/               # Pruebas e intentos deliberados de ataques
│   ├── load/                   # Locustfile para pruebas de carga y concurrencia
│   └── regression/             # Comparación contra snapshots baseline_responses.json
└── presentation/
    └── streamlit_app.py        # Panel interactivo de demo para el cliente
```

---

## 📦 CREDENCIALES DE DEMO — NO USAR EN PRODUCCIÓN

Para la demo interactiva en Streamlit, el selector de roles realiza inicios de sesión genuinos contra la API REST, generando JWT reales que aplican políticas RLS reales. Utilice exactamente estas credenciales de prueba pre-sembradas en el dataset:

| Usuario | Email | Password | Rol / Estado |
|---|---|---|---|
| **Miembro Activo** | `miembro.activo@demo.local` | `Demo2026!Activo` | miembro, al día en pagos |
| **Miembro en Mora** | `miembro.entredicho@demo.local` | `Demo2026!Mora` | miembro, >90 días de mora -> `estado_membresia = entredicho` |
| **Administrador** | `admin.demo@demo.local` | `Demo2026!Admin` | admin |

---

## 🚀 Instrucciones de Despliegue Rápido

### Prerrequisitos

- Docker y Docker Compose instalados.
- [Opcional] `uv` instalado si desea correr pruebas locales fuera de contenedores.

### Pasos para levantar el stack completo

1. **Configurar Variables de Entorno**:
   Copie el archivo de ejemplo y ajuste según sea necesario:
   ```bash
   cp rag-service/.env.example rag-service/.env
   ```

2. **Descargar el Modelo GGUF (Solo para Inferencia Real GGUF)**:
   Si desea correr el modelo real de inteligencia artificial en local en lugar del modo determinista Mock, descargue el modelo GGUF y colóquelo bajo el directorio correspondiente:
   - Modelo recomendado: `llama-2-7b-chat.Q4_K_M.gguf` o similar.
   - Configure `MOCK_LLM=false` y `MODEL_PATH=/app/models/su_modelo.gguf` en el archivo `.env`.

3. **Levantar los Contenedores**:
   Ejecute el comando para compilar y levantar de forma integrada Postgres (pgvector), la API de Litestar, Streamlit y Nginx:
   ```bash
   docker compose -f rag-service/docker-compose.yml up --build -d
   ```

4. **Correr la Ingesta Inicial de Datos de Demo**:
   Una vez que el contenedor de Postgres se encuentre activo y listo:
   - Generar el dataset sintético de 550 miembros e insertarlo en Postgres de forma idempotente:
     ```bash
     docker compose -f rag-service/docker-compose.yml exec litestar-api python3 etl/synthetic_data.py
     docker compose -f rag-service/docker-compose.yml exec litestar-api python3 etl/tabular_ingestor.py
     ```
   - Ingerir los PDFs de prueba:
     ```bash
     docker compose -f rag-service/docker-compose.yml exec litestar-api python3 etl/pdf_ingestor.py
     ```

5. **Acceso a los Servicios**:
   - **Nginx (Proxy Integrado)**: `http://localhost:8080/` (Enruta `/chat/*` y `/auth/*` a Python, y lo demás a Node.js).
   - **Streamlit (Demo Cliente)**: `http://localhost:8501/` (Selector de roles reales, chat conversacional y panel de transparencia).

---

## 🧪 Execution of Automated Tests

Para correr la suite de tests automatizados que aseguran la correctitud de todas las reglas críticas:

```bash
# Instalar dependencias necesarias localmente
uv pip install -r rag-service/src/pyproject.toml

# Ejecutar las pruebas asíncronas con pytest
PYTHONPATH=rag-service/src FORCE_MOCK_DB=true DB_PASSWORD=test JWT_SECRET=test python3 -m pytest rag-service/tests/ -v
```

Todas las pruebas se encuentran configuradas con un mock determinista para asegurar su reproducibilidad instantánea en cualquier entorno sin depender del hardware local.

---

## 🔒 Cifrado en Reposo de Sistema Operativo (LUKS) - Recomendación

Para garantizar la seguridad física absoluta del servidor de producción local (on-premise de 2015), se recomienda encarecidamente instalar el sistema operativo host utilizando cifrado completo de disco con **LUKS** (Linux Unified Key Setup). Esto asegura que en caso de pérdida o acceso físico no autorizado al equipo, el catálogo, las bases de datos y el modelo RAG permanezcan inaccesibles sin la frase de contraseña maestra de arranque.
