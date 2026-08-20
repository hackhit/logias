from abc import ABC, abstractmethod

class InferenceEngine(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, context_chunks: list[dict]) -> str:
        """
        Genera la respuesta dada la consulta (prompt) y los chunks de contexto recuperados.
        """
        pass
