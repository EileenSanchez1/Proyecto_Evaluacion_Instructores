"""Pruebas unitarias de app/config/security.py (JWT y códigos OTP)."""
import jwt
import pytest
from fastapi import HTTPException

from app.config import security


# ---------- Tokens de sesión ----------
def test_crear_y_decodificar_access_token():
    token = security.crear_access_token(7, "a@sena.edu.co", "Aprendiz")
    payload = security.decodificar_token(token)
    assert payload["sub"] == "7"
    assert payload["correo"] == "a@sena.edu.co"
    assert payload["rol"] == "Aprendiz"


def test_token_expirado_lanza_401(monkeypatch):
    monkeypatch.setattr(security, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    token = security.crear_access_token(1, "x@sena.edu.co", "Aprendiz")
    with pytest.raises(HTTPException) as e:
        security.decodificar_token(token)
    assert e.value.status_code == 401
    assert "expirado" in e.value.detail


def test_token_invalido_lanza_401():
    with pytest.raises(HTTPException) as e:
        security.decodificar_token("esto.no.es-un-token")
    assert e.value.status_code == 401


def test_token_firmado_con_otra_clave_es_rechazado():
    falso = jwt.encode({"sub": "1"}, "otra-clave-cualquiera-de-32-caracteres", algorithm="HS256")
    with pytest.raises(HTTPException):
        security.decodificar_token(falso)


# ---------- Token de recuperación ----------
def test_token_recuperacion_valido():
    token = security.crear_token_recuperacion(3, "r@sena.edu.co")
    payload = security.verificar_token_recuperacion(token)
    assert payload["tipo"] == "reset"


def test_token_de_sesion_no_sirve_para_recuperar():
    token = security.crear_access_token(3, "r@sena.edu.co", "Aprendiz")
    with pytest.raises(HTTPException) as e:
        security.verificar_token_recuperacion(token)
    assert e.value.status_code == 401


def test_token_recuperacion_expirado(monkeypatch):
    monkeypatch.setattr(security, "RESET_TOKEN_EXPIRE_MINUTES", -1)
    token = security.crear_token_recuperacion(3, "r@sena.edu.co")
    with pytest.raises(HTTPException) as e:
        security.verificar_token_recuperacion(token)
    assert "expirado" in e.value.detail


def test_token_recuperacion_invalido():
    with pytest.raises(HTTPException):
        security.verificar_token_recuperacion("basura")


# ---------- Códigos OTP ----------
def test_generar_codigo_numerico():
    codigo = security.generar_codigo_numerico(6)
    assert len(codigo) == 6 and codigo.isdigit()


@pytest.mark.parametrize("tipo", ["recuperacion", "instructor", "admin"])
def test_codigo_correcto_se_consume(tipo):
    security.guardar_codigo("User@Sena.edu.co ", "123456", tipo=tipo)
    # El correo se normaliza (mayúsculas / espacios)
    assert security.verificar_codigo("user@sena.edu.co", "123456", tipo=tipo) is True
    # Ya se consumió: no se puede reutilizar
    assert security.verificar_codigo("user@sena.edu.co", "123456", tipo=tipo) is False


def test_codigo_sin_consumir_se_puede_volver_a_usar():
    security.guardar_codigo("a@sena.edu.co", "111111")
    assert security.verificar_codigo("a@sena.edu.co", "111111", consumir=False)
    assert security.verificar_codigo("a@sena.edu.co", "111111", consumir=True)


def test_codigo_incorrecto():
    security.guardar_codigo("a@sena.edu.co", "111111")
    assert security.verificar_codigo("a@sena.edu.co", "999999") is False


def test_codigo_expirado():
    security.guardar_codigo("a@sena.edu.co", "111111", expiracion_minutos=-1)
    assert security.verificar_codigo("a@sena.edu.co", "111111") is False


def test_codigo_inexistente_y_tipo_desconocido():
    assert security.verificar_codigo("nadie@sena.edu.co", "000000") is False
    assert security.verificar_codigo("a@sena.edu.co", "1", tipo="otro") is False


@pytest.mark.parametrize("tipo", ["recuperacion", "instructor", "admin"])
def test_limpiar_codigo(tipo):
    security.guardar_codigo("a@sena.edu.co", "222222", tipo=tipo)
    security.limpiar_codigo("a@sena.edu.co", tipo=tipo)
    assert security.verificar_codigo("a@sena.edu.co", "222222", tipo=tipo) is False


@pytest.mark.parametrize("permitido", [True, False])
def test_log_codigo_debug(monkeypatch, caplog, permitido):
    monkeypatch.setattr(security, "ALLOW_DEBUG_CODES", permitido)
    with caplog.at_level("INFO", logger="app.security"):
        security.log_codigo_debug("admin", "a@sena.edu.co", "654321")
    # El código solo aparece en el log cuando está permitido (desarrollo)
    assert ("654321" in caplog.text) is permitido
