"""Pruebas de integración de los endpoints /login (los 3 portales)."""
from app.config import security
from app.services.login_service import LoginService
from tests.conftest import PASSWORD_OK


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ================= Portal APRENDIZ =================
def test_login_aprendiz_exitoso(client, usuario_aprendiz):
    r = client.post("/login/", json={"correo": usuario_aprendiz.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["usuario"]["rol"] == "Aprendiz"
    assert data["usuario"]["id_aprendiz"] is not None


def test_login_aprendiz_password_incorrecta(client, usuario_aprendiz):
    r = client.post("/login/", json={"correo": usuario_aprendiz.correo, "contrasena": "Mala123!"})
    assert r.status_code == 401


def test_login_aprendiz_correo_invalido(client):
    r = client.post("/login/", json={"correo": "no-es-correo", "contrasena": "x"})
    assert r.status_code == 422


def test_instructor_no_entra_por_portal_aprendiz(client, crear_instructor):
    _, u = crear_instructor()
    r = client.post("/login/", json={"correo": u.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 403
    assert "instructor" in r.json()["detail"]


def test_admin_no_entra_por_portal_aprendiz(client, usuario_admin):
    r = client.post("/login/", json={"correo": usuario_admin.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 403
    assert "administración" in r.json()["detail"]


def test_otro_rol_no_entra_por_portal_aprendiz(client, crear_usuario):
    u = crear_usuario("coord@soy.sena.edu.co", rol="Coordinador")
    # Coordinador se trata como administración
    assert client.post("/login/", json={"correo": u.correo, "contrasena": PASSWORD_OK}).status_code == 403


def test_usuario_aprendiz_sin_registro_de_aprendiz(client, crear_usuario):
    u = crear_usuario("suelto@soy.sena.edu.co", rol="Aprendiz")
    r = client.post("/login/", json={"correo": u.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 403
    assert "vinculado" in r.json()["detail"]


# ================= Portal ADMINISTRADOR (2 pasos) =================
def test_login_admin_dos_pasos(client, usuario_admin):
    r = client.post("/login/admin/iniciar", json={"correo": usuario_admin.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 200
    data = r.json()
    assert data["requiere_codigo"] is True
    assert "codigo_temporal" not in data  # el código nunca se muestra si el correo salió

    codigo = security._codigos_admin[usuario_admin.correo]["codigo"]
    r2 = client.post("/login/admin/verificar", json={"correo": usuario_admin.correo, "codigo": codigo})
    assert r2.status_code == 200
    assert r2.json()["usuario"]["rol"] == "Administrador"


def test_admin_codigo_incorrecto(client, usuario_admin):
    client.post("/login/admin/iniciar", json={"correo": usuario_admin.correo, "contrasena": PASSWORD_OK})
    r = client.post("/login/admin/verificar", json={"correo": usuario_admin.correo, "codigo": "000000x"})
    assert r.status_code == 400


def test_admin_password_incorrecta(client, usuario_admin):
    r = client.post("/login/admin/iniciar", json={"correo": usuario_admin.correo, "contrasena": "Mala123!"})
    assert r.status_code == 401


def test_aprendiz_e_instructor_no_entran_por_portal_admin(client, usuario_aprendiz, crear_instructor, crear_usuario):
    _, inst = crear_instructor()
    coord = crear_usuario("coord@soy.sena.edu.co", rol="Coordinador")
    for u in (usuario_aprendiz, inst, coord):
        r = client.post("/login/admin/iniciar", json={"correo": u.correo, "contrasena": PASSWORD_OK})
        assert r.status_code == 403


def test_admin_correo_falla_muestra_codigo_de_emergencia(client, usuario_admin, monkeypatch):
    import app.services.login_service as ls

    monkeypatch.setattr(ls, "mail_codigo_admin", lambda *_: False)
    monkeypatch.setenv("ALLOW_SHOW_ADMIN_CODE", "true")
    r = client.post("/login/admin/iniciar", json={"correo": usuario_admin.correo, "contrasena": PASSWORD_OK})
    assert r.status_code == 200
    assert r.json()["email_enviado"] is False
    assert "codigo_temporal" in r.json()


def test_admin_correo_falla_sin_emergencia(client, usuario_admin, monkeypatch):
    import app.services.login_service as ls

    monkeypatch.setattr(ls, "mail_codigo_admin", lambda *_: False)
    r = client.post("/login/admin/iniciar", json={"correo": usuario_admin.correo, "contrasena": PASSWORD_OK})
    assert r.json()["email_enviado"] is False
    assert "codigo_temporal" not in r.json()


def test_admin_verificar_con_cuenta_que_no_es_admin(client, usuario_aprendiz):
    security.guardar_codigo(usuario_aprendiz.correo, "123456", tipo="admin")
    r = client.post("/login/admin/verificar", json={"correo": usuario_aprendiz.correo, "codigo": "123456"})
    assert r.status_code == 403


def test_admin_verificar_cuenta_inexistente(client, roles):
    security.guardar_codigo("fantasma@soy.sena.edu.co", "123456", tipo="admin")
    r = client.post("/login/admin/verificar", json={"correo": "fantasma@soy.sena.edu.co", "codigo": "123456"})
    assert r.status_code == 401


# ================= Portal INSTRUCTOR =================
def test_instructor_correo_no_institucional(client):
    r = client.post("/login/instructor/iniciar", json={"correo": "alguien@gmail.com"})
    assert r.status_code == 400


def test_instructor_no_registrado(client, roles):
    r = client.post("/login/instructor/iniciar", json={"correo": "nadie@sena.edu.co"})
    assert r.status_code == 404


def test_instructor_login_normal(client, crear_instructor):
    _, u = crear_instructor()
    r = client.post("/login/instructor/iniciar", json={"correo": u.correo})
    assert r.json()["requiere_crear_password"] is False

    r2 = client.post("/login/instructor", json={"correo": u.correo, "contrasena": PASSWORD_OK})
    assert r2.status_code == 200
    assert r2.json()["usuario"]["rol"] == "Instructor"


def test_instructor_password_incorrecta(client, crear_instructor):
    _, u = crear_instructor()
    r = client.post("/login/instructor", json={"correo": u.correo, "contrasena": "Mala123!"})
    assert r.status_code == 401


def test_instructor_login_correo_no_institucional(client):
    r = client.post("/login/instructor", json={"correo": "x@gmail.com", "contrasena": "x"})
    assert r.status_code == 400


def test_instructor_primer_acceso_completo(client, crear_instructor):
    _, u = crear_instructor("nuevo@sena.edu.co", contrasena=LoginService.PASSWORD_PENDIENTE_MARKER)

    r = client.post("/login/instructor/iniciar", json={"correo": u.correo})
    assert r.json()["requiere_crear_password"] is True

    # Sin crear contraseña no puede hacer login normal
    r_bloq = client.post("/login/instructor", json={"correo": u.correo, "contrasena": "x"})
    assert r_bloq.status_code == 400

    codigo = security._codigos_instructor[u.correo]["codigo"]
    r2 = client.post(
        "/login/instructor/crear-password",
        json={"correo": u.correo, "codigo": codigo, "nueva_contrasena": "Nueva123!"},
    )
    assert r2.status_code == 200
    assert r2.json()["usuario"]["rol"] == "Instructor"


def test_instructor_crear_password_codigo_invalido(client, crear_instructor):
    _, u = crear_instructor("nuevo@sena.edu.co", contrasena=LoginService.PASSWORD_PENDIENTE_MARKER)
    r = client.post(
        "/login/instructor/crear-password",
        json={"correo": u.correo, "codigo": "000000", "nueva_contrasena": "Nueva123!"},
    )
    assert r.status_code == 400


def test_instructor_que_ya_tiene_password_no_puede_recrearla(client, crear_instructor):
    _, u = crear_instructor()
    security.guardar_codigo(u.correo, "123456", tipo="instructor")
    r = client.post(
        "/login/instructor/crear-password",
        json={"correo": u.correo, "codigo": "123456", "nueva_contrasena": "Nueva123!"},
    )
    assert r.status_code == 400


def test_crear_password_correo_no_institucional(client):
    r = client.post(
        "/login/instructor/crear-password",
        json={"correo": "x@gmail.com", "codigo": "1", "nueva_contrasena": "Nueva123!"},
    )
    assert r.status_code == 400


def test_correo_de_instructor_con_rol_distinto(client, session, crear_usuario):
    from app.models.instructor import Instructor

    u = crear_usuario("raro@sena.edu.co", rol="Aprendiz")
    session.add(Instructor(nombre="R", apellido="R", correo=u.correo, telefono="1", id_usuario=u.id_usuario))
    session.commit()
    r = client.post("/login/instructor/iniciar", json={"correo": u.correo})
    assert r.status_code == 403


# ================= Recuperación de contraseña =================
def test_recuperar_siempre_responde_200(client, roles):
    r = client.post("/login/recuperar", json={"correo": "noexiste@soy.sena.edu.co"})
    assert r.status_code == 200


def test_recuperacion_completa(client, usuario_aprendiz):
    client.post("/login/recuperar", json={"correo": usuario_aprendiz.correo})
    codigo = security._codigos_recuperacion[usuario_aprendiz.correo]["codigo"]

    r = client.post("/login/verificar-codigo", json={"correo": usuario_aprendiz.correo, "codigo": codigo})
    assert r.status_code == 200 and r.json()["valido"] is True

    r2 = client.post(
        "/login/restablecer",
        json={"correo": usuario_aprendiz.correo, "codigo": codigo, "nueva_contrasena": "Nueva123!"},
    )
    assert r2.status_code == 200

    r3 = client.post("/login/", json={"correo": usuario_aprendiz.correo, "contrasena": "Nueva123!"})
    assert r3.status_code == 200


def test_verificar_codigo_incorrecto(client):
    r = client.post("/login/verificar-codigo", json={"correo": "a@soy.sena.edu.co", "codigo": "000000"})
    assert r.status_code == 400


def test_restablecer_con_codigo_incorrecto(client, usuario_aprendiz):
    r = client.post(
        "/login/restablecer",
        json={"correo": usuario_aprendiz.correo, "codigo": "000000", "nueva_contrasena": "Nueva123!"},
    )
    assert r.status_code == 400


def test_restablecer_contrasena_debil(client, usuario_aprendiz):
    r = client.post(
        "/login/restablecer",
        json={"correo": usuario_aprendiz.correo, "codigo": "000000", "nueva_contrasena": "debil"},
    )
    assert r.status_code == 422


# ================= Cambio de contraseña autenticado =================
def test_cambiar_password(client, usuario_aprendiz, token_de):
    r = client.post(
        "/login/cambiar-password",
        json={"contrasena_actual": PASSWORD_OK, "nueva_contrasena": "Nueva123!"},
        headers=token_de(usuario_aprendiz),
    )
    assert r.status_code == 200


def test_cambiar_password_actual_incorrecta(client, usuario_aprendiz, token_de):
    r = client.post(
        "/login/cambiar-password",
        json={"contrasena_actual": "Mala123!", "nueva_contrasena": "Nueva123!"},
        headers=token_de(usuario_aprendiz),
    )
    assert r.status_code == 400


def test_cambiar_password_sin_token(client):
    r = client.post(
        "/login/cambiar-password",
        json={"contrasena_actual": PASSWORD_OK, "nueva_contrasena": "Nueva123!"},
    )
    assert r.status_code in (401, 403)
