import os
import json
from pydantic import BaseModel, EmailStr
from litestar import Controller, Post, Body, get
from litestar.exceptions import HTTPException, NotAuthorizedException, PermissionDeniedException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from passlib.hash import argon2

from database.connection import scoped_connection
from api.auth import create_access_token, decode_access_token
from api.middlewares import log_audit_to_db

# Motores de IA
from ai_engine.embeddings import EmbeddingsEngine
from ai_engine.llm import LlamaInferenceEngine
from core.security import heuristic_injection_filter
from core.router import classify_intent
from core.output_validator import validate_output
from core.prompt import assemble_prompt

# Inicializar motores
emb_engine = EmbeddingsEngine()
llm_engine = LlamaInferenceEngine()

# Modelos Pydantic para request/response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChatQueryRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    sources: list[dict]
    estado_membresia: str | None = None

class AuthController(Controller):
    path = "/auth"

    @Post("/login")
    async def login(self, data: Body[LoginRequest]) -> dict:
        """
        Endpoint de inicio de sesión real que valida las credenciales contra la base de datos
        y devuelve un token JWT con el rol y la cédula del miembro.
        """
        # Conexión libre para buscar las credenciales (rol temporal admin)
        async with scoped_connection(user_id="auth_system", user_role="admin") as conn:
            user = await conn.fetchrow(
                "SELECT cedula, nombre, email, password_hash, rol, estado_membresia FROM vista_miembros WHERE email = $1",
                data.email
            )

            if not user:
                # Loggear auditoría fallida
                await log_audit_to_db(None, "LOGIN_FAILED", f"Intento de login fallido para el email: {data.email}")
                raise HTTPException(detail="Credenciales incorrectas", status_code=HTTP_401_UNAUTHORIZED)

            # Verificar contraseña con Argon2
            is_valid = False
            try:
                is_valid = argon2.verify(data.password, user["password_hash"])
            except Exception:
                is_valid = False

            if not is_valid:
                await log_audit_to_db(user["cedula"], "LOGIN_FAILED", f"Contraseña incorrecta para el usuario: {data.email}")
                raise HTTPException(detail="Credenciales incorrectas", status_code=HTTP_401_UNAUTHORIZED)

            # Crear token JWT
            token_data = {
                "sub": user["cedula"],
                "email": user["email"],
                "nombre": user["nombre"],
                "rol": user["rol"],
                "estado_membresia": user["estado_membresia"]
            }
            token = create_access_token(token_data)

            # Registrar auditoría exitosa con await explícito
            await log_audit_to_db(
                user["cedula"],
                "LOGIN_SUCCESS",
                f"Inicio de sesión exitoso. Rol: {user['rol']}. Estado membresía: {user['estado_membresia']}"
            )

            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "cedula": user["cedula"],
                    "nombre": user["nombre"],
                    "email": user["email"],
                    "rol": user["rol"],
                    "estado_membresia": user["estado_membresia"]
                }
            }

class ChatController(Controller):
    path = "/chat"

    @Post("/query")
    async def query(self, scope: Scope, data: Body[ChatQueryRequest]) -> ChatResponse:
        """
        Endpoint de consulta RAG conversacional seguro.
        Aplica:
        1. Decodificación JWT.
        2. Filtro heurístico anti-inyecciones.
        3. Clasificación de intención.
        4. Recuperación semántica de base de datos protegida mediante RLS.
        5. Inferencia local secuencial a través de Llama CPP o modo Mock.
        6. Validador de salida determinista contra alucinaciones.
        7. Auditoría inmutable obligatoria.
        """
        # 1. Obtener cabecera de autenticación si existe
        headers = scope.get("headers", [])
        token = None
        for k, v in headers:
            if k == b"authorization":
                auth_val = v.decode("utf-8")
                if auth_val.lower().startswith("bearer "):
                    token = auth_val[7:]
                break

        user_id = None
        user_role = 'publico'
        estado_membresia = 'activo'

        if token:
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                user_role = payload.get("rol", 'publico')
                # Recalcular el estado de membresía real de la base de datos para prevenir inconsistencias de token expirados
                async with scoped_connection(user_id="auth_system", user_role="admin") as conn:
                    db_user = await conn.fetchrow(
                        "SELECT estado_membresia FROM vista_miembros WHERE cedula = $1", user_id
                    )
                    if db_user:
                        estado_membresia = db_user["estado_membresia"]

        # 2. Filtro de inyección
        if heuristic_injection_filter(data.query):
            await log_audit_to_db(user_id, "BLOCKED_INJECTION", f"Consulta bloqueada por inyección potencial: {data.query}")
            raise HTTPException(detail="Consulta insegura o patrón malicioso detectado.", status_code=HTTP_400_BAD_REQUEST)

        # 3. Enrutador de Intenciones (Capa de intención para optimización)
        intent = classify_intent(data.query)

        # 4. Recuperación Vectorial basada en RLS
        # Realizamos la búsqueda directamente dentro de scoped_connection, garantizando RLS
        chunks = []
        embedding = emb_engine.get_embedding(data.query)

        async with scoped_connection(user_id=user_id, user_role=user_role) as conn:
            # Query pgvector con orden por distancia de coseno
            # Nota: la política RLS se aplicará de forma automática en la base de datos al realizar select.
            # El filtro de intención nos ayuda a priorizar los fragmentos.
            if intent == "pagos" or intent == "reglamentos":
                # Priorizar documentos con palabras clave relacionadas
                rows = await conn.fetch(
                    """
                    SELECT texto, documento_origen, nivel_acceso
                    FROM documentos_vectoriales
                    ORDER BY (embedding <=> $1::vector) ASC
                    LIMIT 4;
                    """,
                    embedding
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT texto, documento_origen, nivel_acceso
                    FROM documentos_vectoriales
                    ORDER BY (embedding <=> $1::vector) ASC
                    LIMIT 3;
                    """,
                    embedding
                )

            chunks = [dict(r) for r in rows]

        # 5. Generación de respuesta con Llama (o Mock LLM)
        response_text = await llm_engine.generate_response(data.query, chunks)

        # 6. Validador de salida contra alucinaciones / fugas
        is_valid_output = validate_output(response_text, chunks)

        if not is_valid_output:
            await log_audit_to_db(
                user_id,
                "OUTPUT_VALIDATION_FAILED",
                f"La salida del modelo contenía entidades alucinadas o no autorizadas. Bloqueado."
            )
            response_text = "Disculpe, no tengo información suficiente y autorizada dentro de su nivel de acceso para responder esa consulta."

        # 7. Registrar auditoría exitosa de consulta
        audit_msg = f"Consulta exitosa RAG. Intent: {intent}. Chunks recuperados: {len(chunks)}. Orígenes: {[c['documento_origen'] for c in chunks]}"
        await log_audit_to_db(user_id, "RAG_QUERY_SUCCESS", audit_msg)

        return ChatResponse(
            response=response_text,
            sources=[{"texto": c["texto"], "documento_origen": c["documento_origen"], "nivel_acceso": c["nivel_acceso"]} for c in chunks],
            estado_membresia=estado_membresia if user_id else None
        )
