import csv
import random
from datetime import datetime, timedelta

def generate_synthetic_data(num_members=550, seed=42):
    random.seed(seed)

    # Nombres y apellidos para generar miembros aleatorios
    nombres = ["Juan", "Pedro", "Carlos", "Luis", "Andres", "Miguel", "Jose", "Francisco", "Manuel", "Antonio",
               "Jesus", "David", "Daniel", "Jorge", "Alexander", "Victor", "Rafael", "Eduardo", "Julio", "Roberto"]
    apellidos = ["Rodriguez", "Gonzalez", "Hernandez", "Diaz", "Perez", "Gomez", "Flores", "Sanches", "Sosa", "Alvarez",
                 "Rondon", "Blanco", "Castillo", "Torres", "Ramirez", "Medina", "Mendoza", "Guzman", "Silva", "Mejia"]

    logias = [
        "Protectora de las Virtudes Nº 1", "Sol de Oriente Nº 2", "Estrella del Sur Nº 3",
        "Esperanza Nº 4", "La Luz Nº 5", "Acacia Nº 6", "Fraternidad Nº 7", "Progreso Nº 8"
    ]

    miembros = []
    pagos = []

    # 1. Agregar los 3 usuarios de demo requeridos obligatoriamente
    # Miembro Activo: al día en pagos (su último pago debe ser reciente, digamos 2026-02-15)
    miembros.append({
        "cedula": "V-11111111",
        "nombre": "Miembro Activo Demo",
        "email": "miembro.activo@demo.local",
        "password_hash": "argon2_mock_hash_activo", # Se procesará en la ingesta o base de datos si es necesario, o usaremos un hash real de Argon2
        "rol": "miembro",
        "fecha_ingreso": "2020-01-15",
        "logia": "Protectora de las Virtudes Nº 1"
    })
    pagos.append({
        "miembro_cedula": "V-11111111",
        "fecha_pago": "2026-02-15",
        "monto": 30.0
    })

    # Miembro en Mora: >90 días de mora (su último pago es antiguo, digamos 2025-10-15; ref es 2026-03-01)
    miembros.append({
        "cedula": "V-22222222",
        "nombre": "Miembro en Mora Demo",
        "email": "miembro.entredicho@demo.local",
        "password_hash": "argon2_mock_hash_mora",
        "rol": "miembro",
        "fecha_ingreso": "2019-05-10",
        "logia": "Sol de Oriente Nº 2"
    })
    pagos.append({
        "miembro_cedula": "V-22222222",
        "fecha_pago": "2025-10-15", # Mora mayor a 90 días respecto a 2026-03-01 (137 días de diferencia)
        "monto": 30.0
    })

    # Administrador
    miembros.append({
        "cedula": "V-33333333",
        "nombre": "Administrador Demo",
        "email": "admin.demo@demo.local",
        "password_hash": "argon2_mock_hash_admin",
        "rol": "admin",
        "fecha_ingreso": "2015-11-20",
        "logia": "La Luz Nº 5"
    })
    # El admin puede o no tener historial de pagos, agreguemos uno reciente
    pagos.append({
        "miembro_cedula": "V-33333333",
        "fecha_pago": "2026-02-20",
        "monto": 50.0
    })

    # Generar el resto de miembros hasta completar num_members
    fecha_referencia = datetime.strptime("2026-03-01", "%Y-%m-%d")

    for i in range(4, num_members + 1):
        cedula_num = 10000000 + i
        cedula = f"V-{cedula_num}"
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        email = f"user_{i}@logias.local"
        rol = "miembro" # La gran mayoría son miembros
        logia = random.choice(logias)

        # Fecha de ingreso entre 1 y 15 años atrás
        antiguedad_dias = random.randint(365, 365 * 15)
        fecha_ingreso_dt = fecha_referencia - timedelta(days=antiguedad_dias)
        fecha_ingreso = fecha_ingreso_dt.strftime("%Y-%m-%d")

        miembros.append({
            "cedula": cedula,
            "nombre": nombre,
            "email": email,
            "password_hash": f"argon2_mock_hash_{i}",
            "rol": rol,
            "fecha_ingreso": fecha_ingreso,
            "logia": logia
        })

        # Generar pagos. Algunos están al día, otros en mora.
        # Caso de mora se decide aleatoriamente (ej. 15% en mora de más de 3 meses, 85% al día)
        en_mora = random.random() < 0.15

        if en_mora:
            # Último pago hace entre 91 y 180 días
            mora_dias = random.randint(91, 180)
            ultimo_pago_dt = fecha_referencia - timedelta(days=mora_dias)
        else:
            # Último pago reciente (dentro de los últimos 90 días)
            mora_dias = random.randint(5, 89)
            ultimo_pago_dt = fecha_referencia - timedelta(days=mora_dias)

        # Podemos registrar más de un pago en el historial para simular realismo
        # Agregamos el último pago
        pagos.append({
            "miembro_cedula": cedula,
            "fecha_pago": ultimo_pago_dt.strftime("%Y-%m-%d"),
            "monto": 30.0
        })

        # Opcionalmente, agregar pagos previos
        num_pagos_previos = random.randint(0, 3)
        current_dt = ultimo_pago_dt
        for _ in range(num_pagos_previos):
            # Pago anterior un mes antes (aprox 30 días)
            current_dt = current_dt - timedelta(days=30)
            if current_dt >= fecha_ingreso_dt:
                pagos.append({
                    "miembro_cedula": cedula,
                    "fecha_pago": current_dt.strftime("%Y-%m-%d"),
                    "monto": 30.0
                })

    return miembros, pagos

def save_to_csv(miembros, pagos, miembros_path, pagos_path):
    # Guardar miembros
    with open(miembros_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["cedula", "nombre", "email", "password_hash", "rol", "fecha_ingreso", "logia"])
        writer.writeheader()
        writer.writerows(miembros)

    # Guardar pagos
    with open(pagos_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["miembro_cedula", "fecha_pago", "monto"])
        writer.writeheader()
        writer.writerows(pagos)

if __name__ == "__main__":
    import os
    os.makedirs("rag-service/data", exist_ok=True)
    miembros, pagos = generate_synthetic_data()
    save_to_csv(miembros, pagos, "rag-service/data/miembros_sinteticos.csv", "rag-service/data/pagos_sinteticos.csv")
    print(f"Dataset sintético generado con éxito. {len(miembros)} miembros y {len(pagos)} pagos guardados.")
