import os
import pytest
import logging
from unittest.mock import MagicMock
from main import check_production_warnings
from core.settings import settings

@pytest.mark.asyncio
async def test_production_warning_log(caplog):
    """
    Verifica que si la variable FECHA_REFERENCIA_MORA está activa,
    se emite un warning claro en los logs advirtiendo que no debe usarse en producción (Prioridad 1.2).
    """
    # Establecer la fecha de referencia en settings
    settings.FECHA_REFERENCIA_MORA = "2026-03-01"

    with caplog.at_level(logging.WARNING):
        await check_production_warnings()

    assert len(caplog.records) > 0
    assert "FECHA_REFERENCIA_MORA" in caplog.text
    assert "NUNCA debe usarse en producción" in caplog.text
