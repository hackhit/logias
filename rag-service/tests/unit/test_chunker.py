import pytest
from etl.chunker import semantic_chunking

def test_semantic_chunking_logic():
    dummy_text = (
        "Capítulo I: Disposiciones Fundamentales\n"
        "Articulo 1. La Gran Logia promueve la moral y el libre pensamiento.\n\n"
        "Capítulo II: De los Deberes\n"
        "Articulo 2. Los miembros deben pagar sus cuotas puntualmente."
    )

    chunks = semantic_chunking(dummy_text, max_chunk_size=150)

    # Validar que dividió semánticamente por cabeceras y no rompió la estructura
    assert len(chunks) >= 2
    assert "Capítulo I" in chunks[0]
    assert "Capítulo II" in chunks[1]
