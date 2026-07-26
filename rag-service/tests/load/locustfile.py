from locust import HttpUser, task, between
import random

class RAGServiceUser(HttpUser):
    wait_time = between(3, 5) # Simula velocidad de lectura humana (3 a 5 segs)

    def on_start(self):
        """
        Al iniciar cada usuario, simulamos un login real para obtener un token JWT,
        o realizamos consultas públicas. El 30% serán públicos y el 70% autenticados.
        """
        self.headers = {}
        self.is_authenticated = random.random() < 0.70

        if self.is_authenticated:
            # Login aleatorio entre Miembro Activo y Administrador
            user_data = random.choice([
                {"email": "miembro.activo@demo.local", "password": "Demo2026!Activo"},
                {"email": "admin.demo@demo.local", "password": "Demo2026!Admin"}
            ])
            try:
                response = self.client.post("/auth/login", json=user_data)
                if response.status_code == 200 or response.status_code == 201:
                    token = response.json().get("access_token")
                    self.headers = {"Authorization": f"Bearer {token}"}
            except Exception:
                pass

    @task(3)
    def query_rag_general(self):
        """
        Realiza consultas legítimas habituales.
        """
        queries = [
            "¿Cuáles son los principios fundamentales de la orden?",
            "¿Dónde puedo consultar el reglamento de reincorporación?",
            "¿Quién es el Gran Maestro?",
            "Necesito saber cómo estar al día con mis cuotas"
        ]
        self.client.post("/chat/query", json={"query": random.choice(queries)}, headers=self.headers)

    @task(1)
    def trigger_rate_limiter_burst(self):
        """
        Intenta enviar ráfagas rápidas para validar que el rate limiter (Token Bucket)
        retorna HTTP 429 de forma controlada y robusta.
        """
        for _ in range(5):
            self.client.post("/chat/query", json={"query": "Ráfaga rápida de estrés"}, headers=self.headers)
