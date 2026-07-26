def assemble_prompt(query: str, context_chunks: list[dict]) -> str:
    """
    Ensambla el prompt estructurado para pasárselo al motor LLM,
    asegurando que se sigan instrucciones estrictas de veracidad basándose en el contexto.
    """
    context_str = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_str += f"[Fragmento {i} - Origen: {chunk.get('documento_origen', 'Desconocido')}]:\n{chunk.get('texto', '')}\n\n"

    full_prompt = (
        "Eres un asistente conversacional RAG privado y seguro para la Gran Logia de la República de Venezuela. "
        "Tu tarea es responder la consulta del usuario basándote UNICAMENTE en los fragmentos de contexto provistos abajo. "
        "Si el contexto no tiene suficiente información para responder o si no estás seguro de la respuesta, responde de forma "
        "segura indicando que no tienes información suficiente para responder.\n\n"
        f"Contexto Autorizado:\n{context_str}"
        f"Consulta: {query}\n\n"
        "Instrucciones Estrictas:\n"
        "1. No menciones nombres, correos, cédulas o fechas que no estén explícitamente escritos en el Contexto Autorizado.\n"
        "2. Sé profesional y respetuoso.\n\n"
        "Respuesta:"
    )
    return full_prompt
