from typing import Optional

from sqlmodel import SQLModel


class AprendizBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    id_ficha: int


class AprendizCreate(AprendizBase):
    contrasena: str


class AprendizRead(AprendizBase):
    id_aprendiz: int


class AprendizUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    id_ficha: Optional[int] = None