from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class RecuperarPasswordRequest(BaseModel):
    correo: EmailStr
    nueva_contrasena: str