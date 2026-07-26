import re

def semantic_chunking(text, max_chunk_size=800, overlap=100):
    """
    Divide un texto denso en fragmentos (chunks) respetando la estructura jerárquica
    de capítulos y artículos, evitando cortar secciones semánticas a la mitad.
    """
    # Expresión regular para detectar Capítulos, Artículos, Secciones o Títulos importantes
    pattern = r"(?i)(capítulo\s+[ivxldcm0-9]+|artículo\s+\d+|sección\s+\d+|disposición\s+\w+)"

    # Dividir el texto por estas cabeceras jerárquicas
    parts = re.split(pattern, text)

    chunks = []
    current_chunk = ""

    # El primer elemento de re.split es el texto antes de la primera coincidencia
    if parts:
        current_chunk = parts[0].strip()

    # Iteramos por las partes encontradas. Cada par (coincidencia, texto_siguiente) se junta.
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i+1].strip() if (i+1) < len(parts) else ""

        section_text = f"{header}\n{body}"

        # Si juntar esta sección supera el límite máximo, guardamos el chunk actual y comenzamos uno nuevo
        if len(current_chunk) + len(section_text) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk)

            # Si una sola sección supera el max_chunk_size por sí sola, la partimos por párrafos o líneas
            if len(section_text) > max_chunk_size:
                paragraphs = section_text.split("\n\n")
                sub_chunk = ""
                for para in paragraphs:
                    if len(sub_chunk) + len(para) > max_chunk_size:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = para
                    else:
                        sub_chunk = f"{sub_chunk}\n\n{para}" if sub_chunk else para
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = section_text
        else:
            current_chunk = f"{current_chunk}\n\n{section_text}" if current_chunk else section_text

    if current_chunk:
        chunks.append(current_chunk)

    # Agregar overlap básico si algún chunk quedó extremadamente corto o si se prefiere mayor densidad de contexto
    # Pero el chunking semántico por artículo es superior para mantener la coherencia del reglamento.
    return [c.strip() for c in chunks if c.strip()]
