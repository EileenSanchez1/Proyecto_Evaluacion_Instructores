from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: dict


class SolicitarRecuperacionRequest(BaseModel):
    correo: EmailStr


class RestablecerPasswordRequest(BaseModel):
    token: str
    nueva_contrasena: str