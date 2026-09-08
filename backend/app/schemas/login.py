from pydantic import BaseModel, EmailStr, field_validator
import re

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: dict

class SolicitarRecuperacionRequest(BaseModel):
    correo: EmailStr

class VerificarCodigoRequest(BaseModel):
    correo: EmailStr
    codigo: str

class RestablecerPasswordRequest(BaseModel):
    correo: EmailStr
    codigo: str
    nueva_contrasena: str

    @field_validator("nueva_contrasena")
    @classmethod
    def validar_contrasena_segura(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Debe contener al menos una mayúscula.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Debe contener al menos una minúscula.")
        if not re.search(r"\d", v):
            raise ValueError("Debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Debe contener al menos un carácter especial.")
        return v

class LoginInstructorRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class VerificarCodigoInstructorRequest(BaseModel):
    correo: EmailStr
    codigo: str