from locust import HttpUser, task, between

class UsuarioSistema(HttpUser):
    wait_time = between(1, 2)  # Pausa de 1 a 2 segundos entre peticiones

    @task(3)
    def consultar_catalogo(self):
        self.client.get("/api/v1/productos/")

    @task(1)
    def consultar_detalle(self):
        self.client.get("/api/v1/productos/1/")
