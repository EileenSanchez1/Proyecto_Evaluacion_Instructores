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

# Almacenamiento en memoria para códigos (en producción usar Redis/DB)
_codigos_recuperacion = {}
_codigos_instructor = {}

def crear_access_token(id_usuario: int, correo: str, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="La sesión ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticación inválido.")

def crear_token_recuperacion(id_usuario: int, correo: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "tipo": "reset",
        "iat": ahora,
        "exp": ahora + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token_recuperacion(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "reset":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido para recuperación.")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El enlace de recuperación ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

# =========================
# CÓDIGOS NUMÉRICOS (Recuperación e Instructor 2FA)
# =========================
def generar_codigo_numerico(longitud: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=longitud))

def guardar_codigo(correo: str, codigo: str, tipo: str = "recuperacion", expiracion_minutos: int = 15):
    expira = datetime.now(timezone.utc) + timedelta(minutes=expiracion_minutos)
    if tipo == "recuperacion":
        _codigos_recuperacion[correo] = {"codigo": codigo, "expira": expira}
    elif tipo == "instructor":
        _codigos_instructor[correo] = {"codigo": codigo, "expira": expira}

def verificar_codigo(correo: str, codigo: str, tipo: str = "recuperacion") -> bool:
    if tipo == "recuperacion":
        datos = _codigos_recuperacion.get(correo)
    elif tipo == "instructor":
        datos = _codigos_instructor.get(correo)
    else:
        return False

    if not datos:
        return False
    if datetime.now(timezone.utc) > datos["expira"]:
        # Limpiar expirado
        if tipo == "recuperacion":
            _codigos_recuperacion.pop(correo, None)
        else:
            _codigos_instructor.pop(correo, None)
        return False
    if datos["codigo"] != codigo:
        return False

    # Consumir código (una sola vez)
    if tipo == "recuperacion":
        _codigos_recuperacion.pop(correo, None)
    else:
        _codigos_instructor.pop(correo, None)
    return True

def limpiar_codigo(correo: str, tipo: str = "recuperacion"):
    if tipo == "recuperacion":
        _codigos_recuperacion.pop(correo, None)
    elif tipo == "instructor":
        _codigos_instructor.pop(correo, None)