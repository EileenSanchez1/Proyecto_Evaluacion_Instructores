import os
import random
import uuid

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN (cambiar por usuarios de prueba de la BD local)
# ══════════════════════════════════════════════════════════════
APRENDIZ_CORREO = os.getenv("LOCUST_APRENDIZ_CORREO", "aprendiz1@soy.sena.edu.co")
APRENDIZ_CONTRASENA = os.getenv("LOCUST_APRENDIZ_CONTRASENA", "Prueba123!")

INSTRUCTOR_CORREO = os.getenv("LOCUST_INSTRUCTOR_CORREO", "instructor1@sena.edu.co")
INSTRUCTOR_CONTRASENA = os.getenv("LOCUST_INSTRUCTOR_CONTRASENA", "Prueba123!")
# El admin tiene segundo factor por correo: Locust no puede iniciar sesión solo.
# Inicia sesión en el frontend, copia el access_token y pégalo aquí (dura 60 min).
# Si se deja vacío, el perfil administrador no se ejecuta.
ADMIN_TOKEN = os.getenv("LOCUST_ADMIN_TOKEN", "")

# Requisito No Funcional: percentil 95 menor a 1.5 segundos
P95_MAXIMO_MS = 1500

# Las pruebas con POST crean datos: solo se permiten contra el servidor local
# (base de datos de pruebas). Contra Render se bloquean automáticamente.
PREFIJO_PRUEBA = "[PRUEBA DE CARGA]"
CALIFICACIONES = (1, 3, 5)  # Nunca / Algunas veces / Siempre


def es_servidor_local(host):
    host = (host or "").lower()
    return "127.0.0.1" in host or "localhost" in host


def verificar(respuesta, codigos=(200,)):
    """Marca la petición como exitosa o fallida según el código HTTP."""
    if respuesta.status_code in codigos:
        respuesta.success()
    else:
        respuesta.failure(f"HTTP {respuesta.status_code}: {respuesta.text[:150]}")


# ══════════════════════════════════════════════════════════════
# USUARIO PRINCIPAL: Aprendiz (el rol con más usuarios concurrentes)
# ══════════════════════════════════════════════════════════════
class UsuarioSistema(HttpUser):
    weight = 6
    wait_time = between(1, 2)  # Pausa de 1 a 2 segundos entre peticiones

    def on_start(self):
        self.instructores = []
        self.preguntas = []
        self.completados = set()
        self.iniciar_sesion()

    def iniciar_sesion(self, nombre="/login/ [aprendiz]"):
        with self.client.post(
            "/login/",
            json={"correo": APRENDIZ_CORREO, "contrasena": APRENDIZ_CONTRASENA},
            name=nombre,
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"Login aprendiz falló (revisar CONFIGURACIÓN): HTTP {r.status_code}")
                raise StopUser()
            datos = r.json()
            r.success()
        self.usuario = datos["usuario"]
        self.headers = {"Authorization": f"Bearer {datos['access_token']}"}
        self.id_aprendiz = self.usuario.get("id_aprendiz")
        self.id_ficha = self.usuario.get("id_ficha")
        self.id_periodo = self.usuario.get("id_periodo")

    def get(self, url, name=None):
        with self.client.get(url, headers=self.headers, name=name, catch_response=True) as r:
            if r.status_code == 401:  # token vencido: se renueva la sesión
                r.success()
                self.iniciar_sesion()
                return None
            verificar(r)
            return r.json() if r.ok else None

    # ---------- GET (equivalentes a catálogo y detalle de la guía) ----------
    @task(3)
    def consultar_catalogo(self):
        datos = self.get("/instructores/")
        if datos:
            self.catalogo = [i["id_instructor"] for i in datos if "id_instructor" in i]

    @task(1)
    def consultar_detalle(self):
        ids = getattr(self, "catalogo", None)
        if ids:
            self.get(f"/instructores/{random.choice(ids)}", name="/instructores/[id]")

    @task(3)
    def consultar_mis_evaluaciones(self):
        self.get(f"/evaluaciones/aprendiz/{self.id_aprendiz}",
                 name="/evaluaciones/aprendiz/[id]")

    @task(2)
    def consultar_instructores_de_mi_ficha(self):
        self.cargar_instructores_ficha()

    @task(2)
    def consultar_preguntas_activas(self):
        datos = self.get("/preguntas/activas")
        if datos:
            self.preguntas = datos

    @task(1)
    def consultar_periodos_activos(self):
        self.get("/periodos/activos")

    @task(1)
    def consultar_notificaciones(self):
        self.get("/notificaciones/")

    def cargar_instructores_ficha(self):
        if not (self.id_ficha and self.id_periodo):
            return
        datos = self.get(f"/ficha-instructores/ficha/{self.id_ficha}/periodo/{self.id_periodo}",
                         name="/ficha-instructores/ficha/[id]/periodo/[id]")
        if datos:
            self.instructores = list({item["id_instructor"] for item in datos})

    # ---------- POST ----------
    @task(1)
    def iniciar_sesion_repetido(self):
        # El login cifra/verifica la contraseña (costoso en CPU): se mide bajo carga
        self.iniciar_sesion(nombre="/login/ [aprendiz - repetido]")

    @task(2)
    def diligenciar_evaluacion(self):
        """Flujo real: POST /evaluaciones/iniciar -> POST /respuestas/bulk."""
        if not es_servidor_local(self.host):
            return
        if not self.instructores:
            self.cargar_instructores_ficha()
        if not self.preguntas:
            self.preguntas = self.get("/preguntas/activas") or []
        pendientes = [i for i in self.instructores if i not in self.completados]
        if not (pendientes and self.preguntas and self.id_periodo):
            return

        id_instructor = random.choice(pendientes)

        with self.client.post(
            "/evaluaciones/iniciar",
            params={"id_aprendiz": self.id_aprendiz, "id_instructor": id_instructor,
                    "id_periodo": self.id_periodo},
            headers=self.headers,
            catch_response=True,
        ) as r:
            if r.status_code == 400:
                # Regla de negocio: ya evaluó a este instructor en el periodo (respuesta esperada)
                self.completados.add(id_instructor)
                r.success()
                return
            verificar(r)
            if not r.ok:
                return
            id_evaluacion = r.json()["id_evaluacion"]

        respuestas = [
            {"id_evaluacion": id_evaluacion, "id_pregunta": p["id_pregunta"],
             "id_instructor": id_instructor, "respuesta": random.choice(CALIFICACIONES),
             "observaciones": None}
            for p in self.preguntas
        ]
        with self.client.post("/respuestas/bulk", json=respuestas, headers=self.headers,
                              catch_response=True) as r:
            verificar(r)
            if r.ok:
                self.completados.add(id_instructor)  # la evaluación queda "Evaluado"

    @task(1)
    def enviar_novedad(self):
        if not es_servidor_local(self.host):
            return
        payload = {
            "nombre": self.usuario.get("nombre") or "Prueba",
            "apellido": self.usuario.get("apellido") or "Carga",
            "correo": APRENDIZ_CORREO,
            "ficha": str(self.id_ficha or "N/A"),
            "mensaje": f"{PREFIJO_PRUEBA} Novedad generada automáticamente por Locust",
        }
        with self.client.post("/novedades/", json=payload, headers=self.headers,
                              name="/novedades/ [aprendiz]", catch_response=True) as r:
            verificar(r)


# ══════════════════════════════════════════════════════════════
# Instructor
# ══════════════════════════════════════════════════════════════
class UsuarioInstructor(HttpUser):
    weight = 2
    wait_time = between(1, 2)

    def on_start(self):
        self.iniciar_sesion()

    def iniciar_sesion(self, nombre="/login/instructor"):
        with self.client.post(
            "/login/instructor",
            json={"correo": INSTRUCTOR_CORREO, "contrasena": INSTRUCTOR_CONTRASENA},
            name=nombre,
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"Login instructor falló (revisar CONFIGURACIÓN): HTTP {r.status_code}")
                raise StopUser()
            datos = r.json()
            r.success()
        self.usuario = datos["usuario"]
        self.headers = {"Authorization": f"Bearer {datos['access_token']}"}
        self.id_instructor = self.usuario.get("id_instructor")

    def get(self, url, name=None):
        with self.client.get(url, headers=self.headers, name=name, catch_response=True) as r:
            if r.status_code == 401:
                r.success()
                self.iniciar_sesion()
                return
            verificar(r)

    @task(3)
    def consultar_mi_promedio(self):
        self.get(f"/reportes/mi-promedio?instructor_id={self.id_instructor}",
                 name="/reportes/mi-promedio")

    @task(2)
    def consultar_mis_evaluaciones(self):
        self.get(f"/reportes/mis-evaluaciones?instructor_id={self.id_instructor}",
                 name="/reportes/mis-evaluaciones")

    @task(1)
    def consultar_mis_fichas(self):
        self.get(f"/ficha-instructores/instructor/{self.id_instructor}",
                 name="/ficha-instructores/instructor/[id]")

    @task(1)
    def iniciar_sesion_repetido(self):
        self.iniciar_sesion(nombre="/login/instructor [repetido]")

    @task(1)
    def enviar_novedad(self):
        if not es_servidor_local(self.host):
            return
        payload = {
            "nombre": self.usuario.get("nombre") or "Prueba",
            "apellido": self.usuario.get("apellido") or "Carga",
            "correo": INSTRUCTOR_CORREO,
            "ficha": "N/A",
            "mensaje": f"{PREFIJO_PRUEBA} Novedad generada automáticamente por Locust",
        }
        with self.client.post("/novedades/", json=payload, headers=self.headers,
                              name="/novedades/ [instructor]", catch_response=True) as r:
            verificar(r)


# ══════════════════════════════════════════════════════════════
# Administrador (módulos Administrador – Instructores y – Reportes)
# Solo se ejecuta si ADMIN_TOKEN tiene valor.
# ══════════════════════════════════════════════════════════════
class UsuarioAdministrador(HttpUser):
    weight = 1
    wait_time = between(1, 2)
    abstract = not ADMIN_TOKEN

    def on_start(self):
        self.headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

    def get(self, url, name=None):
        with self.client.get(url, headers=self.headers, name=name, catch_response=True) as r:
            if r.status_code == 401:
                r.failure("Token de administrador vencido: generar uno nuevo")
                raise StopUser()
            verificar(r)

    @task(3)
    def consultar_dashboard(self):
        self.get("/reportes/dashboard")

    @task(2)
    def consultar_instructores(self):
        self.get("/instructores/?incluir_inactivos=true", name="/instructores/ [admin]")

    @task(2)
    def consultar_historial(self):
        self.get("/reportes/historial")

    @task(1)
    def consultar_pendientes(self):
        self.get("/reportes/pendientes-evaluacion")

    @task(1)
    def crear_y_eliminar_ficha(self):
        """POST /fichas/ y luego DELETE para no dejar datos de prueba."""
        if not es_servidor_local(self.host):
            return
        numero = f"CARGA-{uuid.uuid4().hex[:8]}"
        with self.client.post(
            "/fichas/",
            json={"numero_ficha": numero, "programa": f"{PREFIJO_PRUEBA} Programa temporal",
                  "descripcion": "Creada y eliminada por Locust"},
            headers=self.headers,
            catch_response=True,
        ) as r:
            verificar(r, codigos=(200, 201))
            if not r.ok:
                return
            id_ficha = r.json()["id_ficha"]
        with self.client.delete(f"/fichas/{id_ficha}", headers=self.headers,
                                name="/fichas/[id]", catch_response=True) as r:
            verificar(r)


# ══════════════════════════════════════════════════════════════
# Visitante sin sesión (endpoints públicos)
# ══════════════════════════════════════════════════════════════
class UsuarioPublico(HttpUser):
    weight = 1
    wait_time = between(1, 2)

    @task(3)
    def consultar_fichas(self):
        with self.client.get("/fichas/", catch_response=True) as r:
            verificar(r)

    @task(1)
    def healthcheck(self):
        with self.client.get("/health", catch_response=True) as r:
            verificar(r)


# ══════════════════════════════════════════════════════════════
# Validación del Requisito No Funcional al terminar la prueba
# ══════════════════════════════════════════════════════════════
@events.test_start.add_listener
def al_iniciar(environment, **kwargs):
    modo = "GET + POST" if es_servidor_local(environment.host) else "solo GET (servidor remoto)"
    print(f"[Locust] Host: {environment.host} | Peticiones: {modo}")
    print(f"[Locust] Perfil administrador: {'activo' if ADMIN_TOKEN else 'omitido (sin token)'}")
    print(f"[Locust] Criterio RNF: percentil 95 < {P95_MAXIMO_MS} ms")


@events.quitting.add_listener
def evaluar_requisito(environment, **kwargs):
    total = environment.stats.total
    if total.num_requests == 0:
        print("[Locust] No se ejecutaron peticiones.")
        return

    p95 = total.get_response_time_percentile(0.95)
    print("\n" + "=" * 70)
    print(" RESULTADO DE LA PRUEBA DE CARGA – REQUISITO NO FUNCIONAL DE DESEMPEÑO")
    print("=" * 70)
    print(f" Peticiones totales : {total.num_requests}")
    print(f" Fallos             : {total.num_failures} ({total.fail_ratio * 100:.2f} %)")
    print(f" RPS promedio       : {total.total_rps:.2f}")
    print(f" Tiempo promedio    : {total.avg_response_time:.0f} ms")
    print(f" Percentil 95       : {p95:.0f} ms (máximo permitido {P95_MAXIMO_MS} ms)")
    print("-" * 70)
    print(f" {'Endpoint':<52}{'P95 (ms)':>10}  Estado")
    for entrada in sorted(environment.stats.entries.values(), key=lambda e: e.name):
        p95_ep = entrada.get_response_time_percentile(0.95)
        estado = "OK" if p95_ep < P95_MAXIMO_MS else "LENTO"
        print(f" {entrada.method + ' ' + entrada.name:<52}{p95_ep:>10.0f}  {estado}")
    print("-" * 70)

    if p95 < P95_MAXIMO_MS:
        print(f" CUMPLE: el percentil 95 ({p95:.0f} ms) es menor a 1.5 s")
    else:
        print(f" NO CUMPLE: el percentil 95 ({p95:.0f} ms) supera 1.5 s")
        environment.process_exit_code = 1
    print("=" * 70 + "\n")
