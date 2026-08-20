import os
import pytest
from datetime import datetime, date
from database.mock_connection import MockConnection

def test_mora_calculation_thresholds():
    conn = MockConnection()

    # 1. Al día (89 días de diferencia)
    member_89 = {
        "ultimo_pago": date(2025, 12, 2) # Diferencia con 2026-03-01 es exactamente 89 días
    }
    assert conn._calculate_membership_status(member_89, task_id=0) == "activo"

    # 2. Exactamente el límite de 90 días (90 días de diferencia)
    member_90 = {
        "ultimo_pago": date(2025, 12, 1) # Diferencia con 2026-03-01 es exactamente 90 días
    }
    assert conn._calculate_membership_status(member_90, task_id=0) == "activo"

    # 3. En mora (91 días de diferencia)
    member_91 = {
        "ultimo_pago": date(2025, 11, 30) # Diferencia con 2026-03-01 es exactamente 91 días
    }
    assert conn._calculate_membership_status(member_91, task_id=0) == "entredicho"
