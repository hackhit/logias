import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from passlib.hash import argon2

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
        self.session_vars = {}
        self.client_vars = {}

        hash_activo = argon2.hash("Demo2026!Activo")
        hash_mora = argon2.hash("Demo2026!Mora")
        hash_admin = argon2.hash("Demo2026!Admin")

        self.members = [
            {
                "cedula": "V-11111111",
                "nombre": "Miembro Activo Demo",
                "email": "miembro.activo@demo.local",
                "password_hash": hash_activo,
                "rol": "miembro",
                "fecha_ingreso": datetime.strptime("2020-01-15", "%Y-%m-%d").date(),
                "logia": "Protectora de las Virtudes Nº 1",
                "ultimo_pago": datetime.strptime("2026-02-15", "%Y-%m-%d").date()
            },
            {
                "cedula": "V-22222222",
                "nombre": "Miembro en Mora Demo",
                "email": "miembro.entredicho@demo.local",
                "password_hash": hash_mora,
                "rol": "miembro",
                "fecha_ingreso": datetime.strptime("2019-05-10", "%Y-%m-%d").date(),
                "logia": "Sol de Oriente Nº 2",
                "ultimo_pago": datetime.strptime("2025-10-15", "%Y-%m-%d").date()
            },
            {
                "cedula": "V-33333333",
                "nombre": "Administrador Demo",
                "email": "admin.demo@demo.local",
                "password_hash": hash_admin,
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

    def _calculate_membership_status(self, member, task_id):
        ref_str = self._get_var('app.fecha_referencia_mora', task_id) or '2026-03-01'
        ref_date = datetime.strptime(ref_str, "%Y-%m-%d").date()
        ultimo_pago = member["ultimo_pago"]

        dias_mora = (ref_date - ultimo_pago).days
        if dias_mora > 90:
            return "entredicho"
        return "activo"

    def _get_var(self, name, task_id):
        if task_id in self.client_vars and name in self.client_vars[task_id]:
            return self.client_vars[task_id][name]
        return self.session_vars.get(name)

    async def execute(self, query, *args):
        task_id = id(asyncio.current_task())
        if task_id not in self.client_vars:
            self.client_vars[task_id] = {}

        query_upper = query.upper()

        if "UPDATE AUDITORIA" in query_upper or "DELETE FROM AUDITORIA" in query_upper:
            raise Exception("La tabla de auditoría es inmutable. No se permiten actualizaciones o borrados.")

        if "SET_CONFIG" in query_upper or "SET " in query_upper:
            if len(args) >= 2:
                self.client_vars[task_id][args[0]] = str(args[1])
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
            chunk_hash = args[0]
            exists = any(d["chunk_hash"] == chunk_hash for d in self.documents)
            if "ON CONFLICT" in query_upper and exists:
                return "INSERT 0"
            self.documents.append({
                "chunk_hash": args[0],
                "texto": args[1],
                "embedding": args[2],
                "nivel_acceso": args[3],
                "documento_origen": args[4]
            })
            return "INSERT 1"

        return "EXECUTE 1"

    async def fetchval(self, query, *args):
        query_upper = query.upper()
        if "COUNT(*)" in query_upper:
            if "DOCUMENTOS_VECTORIALES" in query_upper:
                return len(self.documents)
        return 0

    async def fetchrow(self, query, *args):
        task_id = id(asyncio.current_task())
        query_upper = query.upper()
        if "VISTA_MIEMBROS" in query_upper:
            for m in self.members:
                status = self._calculate_membership_status(m, task_id)
                current_role = self._get_var("app.current_user_role", task_id) or "publico"
                current_user_id = self._get_var("app.current_user_id", task_id) or ""

                if current_role != "admin" and m["cedula"] != current_user_id and current_user_id != "auth_system" and current_user_id != "audit_system":
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
        task_id = id(asyncio.current_task())
        query_upper = query.upper()
        if "DOCUMENTOS_VECTORIALES" in query_upper:
            current_role = self._get_var("app.current_user_role", task_id) or "publico"
            current_user_id = self._get_var("app.current_user_id", task_id) or ""

            user_status = "activo"
            for m in self.members:
                if m["cedula"] == current_user_id:
                    user_status = self._calculate_membership_status(m, task_id)
                    break

            visible_docs = []
            for doc in self.documents:
                if current_role == "admin":
                    visible_docs.append(doc)
                elif current_role == "miembro":
                    if user_status == "activo":
                        if doc["nivel_acceso"] in ("publico", "miembro"):
                            visible_docs.append(doc)
                    else:
                        if doc["nivel_acceso"] == "publico":
                            visible_docs.append(doc)
                else:
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
