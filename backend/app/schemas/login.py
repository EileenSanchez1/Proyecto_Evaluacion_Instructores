from typing import Optional, Any
from sqlmodel import SQLModel


class LoginRequest(SQLModel):
    correo: str
    contrasena: str


class LoginResponse(SQLModel):
    access_token: str
    token_type: str
    usuario: dict[str, Any]


class SolicitarRecuperacionRequest(SQLModel):
    correo: str


class RestablecerPasswordRequest(SQLModel):
    token: str
    nueva_contrasena: str
