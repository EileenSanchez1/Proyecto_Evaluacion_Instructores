from typing import Optional

from sqlmodel import SQLModel


class InstructorCreate(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    competencia: str
    foto: Optional[str] = None


class InstructorRead(SQLModel):
    id_instructor: int
    nombre: str
    apellido: str
    correo: str
    telefono: str
    competencia: str
    foto: Optional[str]


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    competencia: Optional[str] = None
    foto: Optional[str] = None