"""Pruebas unitarias de LoginService (contraseñas, validación de login, códigos)."""
import pytest

from app.config import security
from app.services.login_service import LoginService
from tests.conftest import PASSWORD_OK


def test_hash_y_verificacion_de_password():
    h = LoginService.hash_password("Clave123!")
    assert h != "Clave123!"
    assert LoginService.verificar_password("Clave123!", h)
    assert not LoginService.verificar_password("otra", h)


@pytest.mark.parametrize(
    "clave, esperado",
    [
        ("Ab1!", "8 caracteres"),
        ("abcdefg1!", "mayúscula"),
        ("ABCDEFG1!", "minúscula"),
        ("Abcdefgh!", "número"),
        ("Abcdefg12", "especial"),
    ],
)
def test_contrasena_insegura(clave, esperado):
    ok, msg = LoginService.validar_contrasena_segura(clave)
    assert ok is False
    assert esperado in msg


def test_contrasena_segura():
    assert LoginService.validar_contrasena_segura("Clave123!") == (True, "Contraseña segura.")


def test_validar_login_exitoso(session, usuario_aprendiz):
    usuario, msg = LoginService.validar_login(session, "  APRENDIZ@soy.sena.edu.co ", PASSWORD_OK)
    assert usuario is not None
    assert msg == "Inicio de sesión exitoso"


def test_validar_login_correo_inexistente(session, roles):
    usuario, msg = LoginService.validar_login(session, "no@existe.co", PASSWORD_OK)
    assert usuario is None and "incorrectos" in msg


def test_validar_login_password_incorrecta(session, usuario_aprendiz):
    usuario, msg = LoginService.validar_login(session, usuario_aprendiz.correo, "Mala123!")
    assert usuario is None and "incorrectos" in msg


def test_validar_login_cuenta_inactiva(session, crear_usuario):
    crear_usuario("inactivo@soy.sena.edu.co", activo=False)
    usuario, msg = LoginService.validar_login(session, "inactivo@soy.sena.edu.co", PASSWORD_OK)
    assert usuario is None and "inactiva" in msg


def test_buscar_por_correo(session, usuario_aprendiz):
    assert LoginService.buscar_por_correo(session, "APRENDIZ@soy.sena.edu.co").id_usuario == usuario_aprendiz.id_usuario
    assert LoginService.buscar_por_correo(session, "nadie@x.co") is None


def test_restablecer_password(session, usuario_aprendiz):
    usuario, msg = LoginService.restablecer_password(session, usuario_aprendiz, "Nueva123!")
    assert LoginService.verificar_password("Nueva123!", usuario.contrasena)
    assert "actualizada" in msg


def test_instructor_necesita_crear_password(session, crear_instructor):
    crear_instructor("nuevo@sena.edu.co", contrasena=LoginService.PASSWORD_PENDIENTE_MARKER)
    crear_instructor("viejo@sena.edu.co", contrasena=PASSWORD_OK)
    assert LoginService.instructor_necesita_crear_password(session, "nuevo@sena.edu.co") is True
    assert LoginService.instructor_necesita_crear_password(session, "viejo@sena.edu.co") is False
    assert LoginService.instructor_necesita_crear_password(session, "nadie@sena.edu.co") is False


def test_establecer_password_instructor(session, crear_instructor):
    crear_instructor("nuevo@sena.edu.co", contrasena=LoginService.PASSWORD_PENDIENTE_MARKER)
    usuario, _ = LoginService.establecer_password_instructor(session, "nuevo@sena.edu.co", "Nueva123!")
    assert usuario is not None
    assert LoginService.establecer_password_instructor(session, "nuevo@sena.edu.co", "debil")[0] is None
    assert LoginService.establecer_password_instructor(session, "nadie@sena.edu.co", "Nueva123!")[0] is None


def test_enviar_codigos_guardan_el_otp(correo_falso):
    c1 = LoginService.enviar_codigo_recuperacion("A@sena.edu.co")
    c2 = LoginService.enviar_codigo_instructor("b@sena.edu.co")
    c3, ok = LoginService.enviar_codigo_admin("c@sena.edu.co")
    assert ok is True
    assert security.verificar_codigo("a@sena.edu.co", c1, tipo="recuperacion")
    assert security.verificar_codigo("b@sena.edu.co", c2, tipo="instructor")
    assert security.verificar_codigo("c@sena.edu.co", c3, tipo="admin")
    assert len(correo_falso) == 3


def test_enviar_codigo_admin_cuando_falla_el_correo(monkeypatch):
    import app.services.login_service as ls

    def _falla(*_):
        raise ConnectionError("SMTP caído")

    monkeypatch.setattr(ls, "mail_codigo_admin", _falla)
    codigo, ok = LoginService.enviar_codigo_admin("c@sena.edu.co")
    assert ok is False
    # Aunque el correo falle, el código queda guardado
    assert security.verificar_codigo("c@sena.edu.co", codigo, tipo="admin")


def test_enviar_codigos_sin_servicio_de_correo(monkeypatch):
    import app.services.login_service as ls

    monkeypatch.setattr(ls, "mail_codigo_recuperacion", None)
    monkeypatch.setattr(ls, "mail_codigo_instructor", None)
    monkeypatch.setattr(ls, "mail_codigo_admin", None)
    monkeypatch.setenv("ALLOW_SHOW_ADMIN_CODE", "true")
    assert LoginService.enviar_codigo_recuperacion("a@sena.edu.co")
    assert LoginService.enviar_codigo_instructor("b@sena.edu.co")
    assert LoginService.enviar_codigo_admin("c@sena.edu.co")[1] is False
