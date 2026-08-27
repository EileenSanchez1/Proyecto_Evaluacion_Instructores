from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel


class UsuarioBase(SQLModel):
    nombre: str
    apellido: str
    correo: EmailStr
    id_rol: int
    foto: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    contrasena: str


class UsuarioRead(SQLModel):
    id_usuario: int
    nombre: str
    apellido: str
    correo: EmailStr
    id_rol: int
    foto: Optional[str] = None
    activo: bool
    fecha_creacion: datetime


class UsuarioUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    id_rol: Optional[int] = None
    foto: Optional[str] = None
    activo: Optional[bool] = None