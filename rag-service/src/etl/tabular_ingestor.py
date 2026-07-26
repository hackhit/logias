import os
import asyncio
import polars as pl
import asyncpg
from passlib.hash import argon2
from core.settings import settings

DEMO_PASSWORDS = {
    "miembro.activo@demo.local": "Demo2026!Activo",
    "miembro.entredicho@demo.local": "Demo2026!Mora",
    "admin.demo@demo.local": "Demo2026!Admin"
}

def get_argon2_hash(email, mock_hash):
    if email in DEMO_PASSWORDS:
        return argon2.hash(DEMO_PASSWORDS[email])
    else:
        return "$argon2id$v=19$m=65536,t=3,p=4$6Fsh/H67T/5+FhXlH1K5rA$tWpB/V6Fv3GZ1xS9wE8S/Uv+J8Eom5GgAorvS/4pC3M"

async def ingest_tabular_data(miembros_csv_path, pagos_csv_path):
    print("Iniciando ingesta de datos tabulares con Polars (Lazy)...")

    df_miembros_lazy = pl.scan_csv(miembros_csv_path)
    df_pagos_lazy = pl.scan_csv(pagos_csv_path)

    df_miembros = df_miembros_lazy.collect()
    df_pagos = df_pagos_lazy.collect()

    # Uso estricto de settings de producción sin passwords por defecto hardcodeados
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )

    try:
        print(f"Insertando/Actualizando {df_miembros.height} miembros...")
        async with conn.transaction():
            for row in df_miembros.iter_rows(named=True):
                pwd_hash = get_argon2_hash(row["email"], row["password_hash"])

                await conn.execute(
                    """
                    INSERT INTO miembros (cedula, nombre, email, password_hash, rol, fecha_ingreso, logia)
                    VALUES ($1, $2, $3, $4, $5, CAST($6 AS DATE), $7)
                    ON CONFLICT (cedula) DO UPDATE
                    SET nombre = EXCLUDED.nombre,
                        email = EXCLUDED.email,
                        password_hash = EXCLUDED.password_hash,
                        rol = EXCLUDED.rol,
                        fecha_ingreso = EXCLUDED.fecha_ingreso,
                        logia = EXCLUDED.logia;
                    """,
                    row["cedula"],
                    row["nombre"],
                    row["email"],
                    pwd_hash,
                    row["rol"],
                    row["fecha_ingreso"],
                    row["logia"]
                )

        print(f"Insertando {df_pagos.height} registros de pago de forma idempotente...")
        async with conn.transaction():
            for row in df_pagos.iter_rows(named=True):
                await conn.execute(
                    """
                    INSERT INTO pagos (miembro_cedula, fecha_pago, monto)
                    VALUES ($1, CAST($2 AS DATE), $3)
                    ON CONFLICT (miembro_cedula, fecha_pago) DO NOTHING;
                    """,
                    row["miembro_cedula"],
                    row["fecha_pago"],
                    float(row["monto"])
                )

        print("Ingesta tabular completada con éxito de forma idempotente.")

    except Exception as e:
        print(f"Error durante la ingesta: {e}")
        raise e
    finally:
        await conn.close()

if __name__ == "__main__":
    import sys
    m_path = "rag-service/data/miembros_sinteticos.csv"
    p_path = "rag-service/data/pagos_sinteticos.csv"
    if len(sys.argv) > 2:
        m_path = sys.argv[1]
        p_path = sys.argv[2]

    try:
        asyncio.run(ingest_tabular_data(m_path, p_path))
    except Exception as err:
        print(f"No se pudo completar la ingesta de pagos: {err}.")
