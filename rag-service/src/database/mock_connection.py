import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

# Simulación en memoria de base de datos para pruebas/entornos sin Postgres real
class MockRecord(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class MockTransaction:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockConnection:
    def __init__(self):
        self.session_vars = {
            'app.current_user_role': 'publico',
            'app.current_user_id': '',
            'app.fecha_referencia_mora': '2026-03-01'
        }

        # Semilla de miembros sintéticos de prueba
        self.members = [
            {
                "cedula": "V-11111111",
                "nombre": "Miembro Activo Demo",
                "email": "miembro.activo@demo.local",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$6Fsh/H67T/5+FhXlH1K5rA$tWpB/V6Fv3GZ1xS9wE8S/Uv+J8Eom5GgAorvS/4pC3M",
                "rol": "miembro",
                "fecha_ingreso": datetime.strptime("2020-01-15", "%Y-%m-%d").date(),
                "logia": "Protectora de las Virtudes Nº 1",
                "ultimo_pago": datetime.strptime("2026-02-15", "%Y-%m-%d").date()
            },
            {
                "cedula": "V-22222222",
                "nombre": "Miembro en Mora Demo",
                "email": "miembro.entredicho@demo.local",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$6Fsh/H67T/5+FhXlH1K5rA$tWpB/V6Fv3GZ1xS9wE8S/Uv+J8Eom5GgAorvS/4pC3M",
                "rol": "miembro",
                "fecha_ingreso": datetime.strptime("2019-05-10", "%Y-%m-%d").date(),
                "logia": "Sol de Oriente Nº 2",
                "ultimo_pago": datetime.strptime("2025-10-15", "%Y-%m-%d").date()
            },
            {
                "cedula": "V-33333333",
                "nombre": "Administrador Demo",
                "email": "admin.demo@demo.local",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$6Fsh/H67T/5+FhXlH1K5rA$tWpB/V6Fv3GZ1xS9wE8S/Uv+J8Eom5GgAorvS/4pC3M",
                "rol": "admin",
                "fecha_ingreso": datetime.strptime("2015-11-20", "%Y-%m-%d").date(),
                "logia": "La Luz Nº 5",
                "ultimo_pago": datetime.strptime("2026-02-20", "%Y-%m-%d").date()
            }
        ]

        self.documents = []
        self.audit_log = []

    def transaction(self):
        return MockTransaction()

    def _calculate_membership_status(self, member):
        # Calcular regla de mora de 90 días
        ref_str = self.session_vars.get('app.fecha_referencia_mora', '2026-03-01')
        ref_date = datetime.strptime(ref_str, "%Y-%m-%d").date()
        ultimo_pago = member["ultimo_pago"]

        dias_mora = (ref_date - ultimo_pago).days
        if dias_mora > 90:
            return "entredicho"
        return "activo"

    async def execute(self, query, *args):
        query_upper = query.upper()
        if "SET_CONFIG" in query_upper or "SET " in query_upper:
            # Capturar set_config o set local
            if len(args) >= 2:
                self.session_vars[args[0]] = str(args[1])
            return "SELECT 1"

        if "INSERT INTO AUDITORIA" in query_upper:
            self.audit_log.append({
                "usuario_id": args[0],
                "tipo_consulta": args[1],
                "resultado": args[2]
            })
            return "INSERT 1"

        if "DELETE FROM DOCUMENTOS_VECTORIALES" in query_upper:
            self.documents = []
            return "DELETE 0"

        if "INSERT INTO DOCUMENTOS_VECTORIALES" in query_upper:
            # args: chunk_hash, texto, embedding, nivel_acceso, documento_origen
            self.documents.append({
                "chunk_hash": args[0],
                "texto": args[1],
                "embedding": args[2],
                "nivel_acceso": args[3],
                "documento_origen": args[4]
            })
            return "INSERT 1"

        return "EXECUTE 1"

    async def fetchrow(self, query, *args):
        query_upper = query.upper()
        if "VISTA_MIEMBROS" in query_upper:
            # Buscar miembro por email o cédula
            for m in self.members:
                status = self._calculate_membership_status(m)
                # Simular RLS en miembros: un miembro ordinario solo se ve a sí mismo, admin ve a todos
                current_role = self.session_vars.get("app.current_user_role", "publico")
                current_user_id = self.session_vars.get("app.current_user_id", "")

                if current_role != "admin" and m["cedula"] != current_user_id and current_user_id != "auth_system":
                    continue

                if len(args) > 0 and (m["email"] == args[0] or m["cedula"] == args[0]):
                    return MockRecord({
                        "cedula": m["cedula"],
                        "nombre": m["nombre"],
                        "email": m["email"],
                        "password_hash": m["password_hash"],
                        "rol": m["rol"],
                        "fecha_ingreso": m["fecha_ingreso"],
                        "logia": m["logia"],
                        "estado_membresia": status
                    })
        return None

    async def fetch(self, query, *args):
        query_upper = query.upper()
        if "DOCUMENTOS_VECTORIALES" in query_upper:
            # Aplicar Row Level Security (RLS) en memoria
            current_role = self.session_vars.get("app.current_user_role", "publico")
            current_user_id = self.session_vars.get("app.current_user_id", "")

            # Obtener estado de membresía del usuario actual
            user_status = "activo"
            for m in self.members:
                if m["cedula"] == current_user_id:
                    user_status = self._calculate_membership_status(m)
                    break

            visible_docs = []
            for doc in self.documents:
                # Aplicar regla de visibilidad según rol
                if current_role == "admin":
                    visible_docs.append(doc)
                elif current_role == "miembro":
                    if user_status == "activo":
                        if doc["nivel_acceso"] in ("publico", "miembro"):
                            visible_docs.append(doc)
                    else:
                        # Degradado por mora
                        if doc["nivel_acceso"] == "publico":
                            visible_docs.append(doc)
                else:
                    # Público
                    if doc["nivel_acceso"] == "publico":
                        visible_docs.append(doc)

            return [MockRecord(d) for d in visible_docs]

        return []

class MockPool:
    def __init__(self):
        self.conn = MockConnection()

    @asynccontextmanager
    async def acquire(self):
        yield self.conn

    async def close(self):
        pass
