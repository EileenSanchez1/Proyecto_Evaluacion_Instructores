from datetime import datetime, timedelta, timezone
import os
import random
import string

import jwt
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CAMBIAR_ESTA_CLAVE_EN_ENV")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
RESET_TOKEN_EXPIRE_MINUTES = 30

_codigos_recuperacion = {}
_codigos_instructor = {}


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
