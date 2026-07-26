import os
import asyncio
from ai_engine.engine_interface import InferenceEngine

# Variable global para cargar LlamaCpp una única vez en memoria
_LLM_INSTANCE = None

class LlamaInferenceEngine(InferenceEngine):
    def __init__(self, mock_mode: bool = None):
        # Determinar si activamos el modo Mock
        if mock_mode is None:
            self.mock_mode = os.getenv("MOCK_LLM", "true").lower() == "true"
        else:
            self.mock_mode = mock_mode

        self.model_path = os.getenv("MODEL_PATH", "/app/models/llama-2-7b-chat.Q4_K_M.gguf")

        # Cola asíncrona de un solo consumidor para procesar peticiones secuencialmente
        self.queue = asyncio.Queue()
        self.worker_task = None

        if not self.mock_mode:
            # Inicializar el modelo Llama real (con carga diferida al primer uso)
            self._init_llama_lazy()

    def _init_llama_lazy(self):
        global _LLM_INSTANCE
        if _LLM_INSTANCE is None:
            print(f"Cargando modelo GGUF en memoria (CPU-only): {self.model_path}...")
            try:
                from llama_cpp import Llama
                _LLM_INSTANCE = Llama(
                    model_path=self.model_path,
                    n_ctx=2048,
                    n_threads=4,
                    verbose=False
                )
                print("Modelo cargado exitosamente en memoria.")
            except Exception as e:
                print(f"Error crítico al cargar Llama CPP: {e}. Activando fallback a modo Mock.")
                self.mock_mode = True

    def start_worker(self):
        """Inicia el worker consumidor de la cola."""
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._queue_worker())
            print("Worker de cola de inferencia iniciado con éxito.")

    async def _queue_worker(self):
        """Worker asíncrono secuencial de un solo consumidor."""
        while True:
            try:
                # Esperar la siguiente petición
                prompt, context_chunks, future = await self.queue.get()

                # Procesar la inferencia en un executor (thread pool) para no bloquear el loop asíncrono
                loop = asyncio.get_running_loop()

                if self.mock_mode:
                    # En modo mock es instantáneo pero respetamos la ejecución en executor
                    result = await loop.run_in_executor(
                        None,
                        self._process_mock_inference,
                        prompt,
                        context_chunks
                    )
                else:
                    # Ejecutar inferencia de Llama en el pool de hilos
                    result = await loop.run_in_executor(
                        None,
                        self._process_llama_inference,
                        prompt,
                        context_chunks
                    )

                future.set_result(result)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en el worker de inferencia: {e}")
                if not future.done():
                    future.set_exception(e)
                self.queue.task_done()

    def _process_mock_inference(self, prompt: str, context_chunks: list[dict]) -> str:
        """
        Genera una respuesta 100% determinista a partir de los chunks recuperados.
        Este diseño es obligatorio para garantizar tests reproducibles sin variabilidad del LLM.
        """
        n_sources = len(context_chunks)

        if n_sources == 0:
            return "Basado en la información disponible (0 fuente(s) consultadas dentro de su nivel de acceso): No se encontraron documentos relevantes autorizados para responder su consulta."

        sources_summary = []
        for i, chunk in enumerate(context_chunks, 1):
            text = chunk.get("texto", "")
            doc_name = chunk.get("documento_origen", "Desconocido")
            # Truncar el chunk para la respuesta
            truncated_text = text[:150].replace("\n", " ") + "..." if len(text) > 150 else text.replace("\n", " ")
            sources_summary.append(f"[{i}] Fuente '{doc_name}': {truncated_text}")

        summary_str = "\n".join(sources_summary)

        # Respuesta estructurada y predecible
        response = f"Basado en la información disponible ({n_sources} fuente(s) consultadas dentro de su nivel de acceso):\n{summary_str}"
        return response

    def _process_llama_inference(self, prompt: str, context_chunks: list[dict]) -> str:
        """
        Invoca el modelo GGUF local real en el thread pool.
        """
        global _LLM_INSTANCE
        if _LLM_INSTANCE is None:
            self._init_llama_lazy()

        # Unir el contexto
        context_text = "\n\n".join([c.get("texto", "") for c in context_chunks])

        # Ensamblar prompt con contexto
        full_prompt = (
            "Usa los siguientes fragmentos de contexto para responder la pregunta de forma concisa. "
            "Si no sabes la respuesta o no está en el contexto, di que no tienes información suficiente para responder.\n\n"
            f"Contexto:\n{context_text}\n\n"
            f"Pregunta: {prompt}\n\n"
            "Respuesta:"
        )

        # Generar
        response_dict = _LLM_INSTANCE(
            full_prompt,
            max_tokens=256,
            temperature=0.0, # Cero para determinismo relativo
            stop=["Pregunta:", "Contexto:", "\n\n"]
        )

        return response_dict["choices"][0]["text"].strip()

    async def generate_response(self, prompt: str, context_chunks: list[dict]) -> str:
        """
        Pone la petición en la cola y espera secuencialmente el resultado.
        """
        # Asegurar que el worker esté corriendo
        self.start_worker()

        # Crear un Future para recibir el resultado
        future = asyncio.get_running_loop().create_future()

        # Insertar en la cola
        await self.queue.put((prompt, context_chunks, future))

        # Esperar y retornar el resultado
        return await future
