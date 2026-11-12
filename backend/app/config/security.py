from datetime import datetime, timedelta, timezone
import os
import random
import string
import logging

import jwt
from fastapi import HTTPException, status

logger = logging.getLogger("app.security")

# En producción: definir JWT_SECRET_KEY fuerte en .env (mín. 32 caracteres).
_raw_secret = (os.getenv("JWT_SECRET_KEY") or "").strip()
_default_inseguro = "CAMBIAR_ESTA_CLAVE_EN_ENV"
ENV_NAME = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development").strip().lower()
IS_PRODUCTION = ENV_NAME in ("production", "prod", "staging")

if not _raw_secret or _raw_secret == _default_inseguro:
    if IS_PRODUCTION:
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurada o usa el valor por defecto. "
            "Defina una clave aleatoria de al menos 32 caracteres en el entorno."
        )
    SECRET_KEY = _default_inseguro
    logger.warning(
        "JWT_SECRET_KEY no configurada: usando valor de desarrollo inseguro. "
        "No usar en producción."
    )
else:
    if len(_raw_secret) < 32 and IS_PRODUCTION:
        raise RuntimeError("JWT_SECRET_KEY debe tener al menos 32 caracteres en producción.")
    SECRET_KEY = _raw_secret

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))

# Solo en desarrollo: permitir imprimir códigos en consola si SMTP falla
ALLOW_DEBUG_CODES = (
    not IS_PRODUCTION
    and (os.getenv("ALLOW_DEBUG_CODES", "true").strip().lower() in ("1", "true", "yes", "on"))
)

_codigos_recuperacion = {}
_codigos_instructor = {}
_codigos_admin = {}


def _norm_correo(correo: str) -> str:
    return (correo or "").strip().lower()


def crear_access_token(id_usuario: int, correo: str, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido.",
        )


def crear_token_recuperacion(id_usuario: int, correo: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "tipo": "reset",
        "iat": ahora,
        "exp": ahora + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token_recuperacion(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "reset":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido para recuperación.",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El enlace de recuperación ha expirado.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )


def generar_codigo_numerico(longitud: int = 6) -> str:
    return "".join(random.choices(string.digits, k=longitud))


def guardar_codigo(
    correo: str,
    codigo: str,
    tipo: str = "recuperacion",
    expiracion_minutos: int = 15,
):
    key = _norm_correo(correo)
    expira = datetime.now(timezone.utc) + timedelta(minutes=expiracion_minutos)
    entry = {"codigo": str(codigo).strip(), "expira": expira, "verificado": False}
    if tipo == "recuperacion":
        _codigos_recuperacion[key] = entry
    elif tipo == "instructor":
        _codigos_instructor[key] = entry
    elif tipo == "admin":
        _codigos_admin[key] = entry


def verificar_codigo(
    correo: str,
    codigo: str,
    tipo: str = "recuperacion",
    consumir: bool = True,
) -> bool:
    """
    consumir=False → solo valida (paso "Verificar código" de la UI).
    consumir=True  → valida y borra el código (cambiar contraseña / primer acceso).
    """
    key = _norm_correo(correo)
    codigo = str(codigo or "").strip()

    if tipo == "recuperacion":
        store = _codigos_recuperacion
    elif tipo == "instructor":
        store = _codigos_instructor
    elif tipo == "admin":
        store = _codigos_admin
    else:
        return False

    datos = store.get(key)
    if not datos:
        return False

    if datetime.now(timezone.utc) > datos["expira"]:
        store.pop(key, None)
        return False

    if datos["codigo"] != codigo:
        return False

    if consumir:
        store.pop(key, None)
    else:
        datos["verificado"] = True
        store[key] = datos

    return True


def limpiar_codigo(correo: str, tipo: str = "recuperacion"):
    key = _norm_correo(correo)
    if tipo == "recuperacion":
        _codigos_recuperacion.pop(key, None)
    elif tipo == "instructor":
        _codigos_instructor.pop(key, None)
    elif tipo == "admin":
        _codigos_admin.pop(key, None)


def log_codigo_debug(tipo: str, correo: str, codigo: str) -> None:
    """Solo en desarrollo y si ALLOW_DEBUG_CODES=true. Nunca en producción."""
    if ALLOW_DEBUG_CODES:
        logger.warning(
            "[DEBUG] Código %s generado para %s (solo desarrollo): %s",
            tipo,
            correo,
            codigo,
        )
    else:
        logger.info("Código %s generado para %s (no se imprime el valor).", tipo, correo)
