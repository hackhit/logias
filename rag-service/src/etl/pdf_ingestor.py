import os
import hashlib
import asyncio
import pdfplumber
import asyncpg
from core.settings import settings
from etl.chunker import semantic_chunking

# Importación diferida del motor de embeddings para evitar import loops
def get_embeddings_engine():
    from ai_engine.embeddings import EmbeddingsEngine
    return EmbeddingsEngine()

def extract_text_from_pdf(pdf_path):
    """
    Usa pdfplumber (licencia permisiva MIT) para extraer el texto completo de un PDF.
    """
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
    return "\n".join(text_content)

async def ingest_pdfs_from_dir(directory, nivel_acceso):
    """
    Procesa todos los archivos PDF en el directorio de manera idempotente.
    """
    if not os.path.exists(directory):
        print(f"La ruta {directory} no existe.")
        return

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No se encontraron archivos PDF en {directory}")
        return

    print(f"Iniciando ingesta de {len(pdf_files)} PDFs en nivel '{nivel_acceso}'...")

    # Inicializar embeddings
    emb_engine = get_embeddings_engine()

    # Uso estricto de settings de producción sin passwords por defecto hardcodeados
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )

    try:
        for pdf_name in pdf_files:
            pdf_path = os.path.join(directory, pdf_name)
            print(f"Procesando {pdf_name}...")

            # Extraer texto
            full_text = extract_text_from_pdf(pdf_path)
            if not full_text.strip():
                print(f"Advertencia: PDF vacío o sin texto legible {pdf_name}")
                continue

            # Generar chunks semánticos
            chunks = semantic_chunking(full_text)
            print(f"PDF dividido en {len(chunks)} chunks semánticos.")

            async with conn.transaction():
                for chunk in chunks:
                    chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                    embedding = emb_engine.get_embedding(chunk)

                    await conn.execute(
                        """
                        INSERT INTO documentos_vectoriales (chunk_hash, texto, embedding, nivel_acceso, documento_origen)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (chunk_hash) DO NOTHING;
                        """,
                        chunk_hash,
                        chunk,
                        embedding,
                        nivel_acceso,
                        pdf_name
                    )
            print(f"Ingesta completada e indexada para: {pdf_name}")

    except Exception as e:
        print(f"Error en la ingesta de PDFs de {directory}: {e}")
        raise e
    finally:
        await conn.close()

async def run_full_pdf_ingest():
    public_dir = "rag-service/data/pdfs/publico"
    private_dir = "rag-service/data/pdfs/miembro"

    await ingest_pdfs_from_dir(public_dir, "publico")
    await ingest_pdfs_from_dir(private_dir, "miembro")

if __name__ == "__main__":
    try:
        asyncio.run(run_full_pdf_ingest())
    except Exception as err:
        print(f"No se pudo completar la ingesta de PDFs directamente: {err}. Nota: Esto es normal si PostgreSQL no está levantado en este paso.")
