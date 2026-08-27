from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import HTTPException, status


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "CAMBIAR_ESTA_CLAVE_EN_ENV"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def crear_access_token(
    id_usuario: int,
    correo: str,
    rol: str
) -> str:

    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decodificar_token(token: str) -> dict:

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido."
        )


RESET_TOKEN_EXPIRE_MINUTES = 30


def crear_token_recuperacion(id_usuario: int, correo: str) -> str:
    """
    Token de un solo propósito (tipo=reset) y vida corta,
    para el enlace de recuperación de contraseña (HU-004).
    """

    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "correo": correo,
        "tipo": "reset",
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=RESET_TOKEN_EXPIRE_MINUTES
        )
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verificar_token_recuperacion(token: str) -> dict:
    """
    Decodifica el token de recuperación y exige que sea
    específicamente de tipo 'reset' (no un access_token normal).
    """

    payload = decodificar_token(token)

    if payload.get("tipo") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido."
        )

    return payload