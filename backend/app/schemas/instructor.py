from typing import Optional

from sqlmodel import SQLModel


class InstructorBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    competencia: str
    foto: Optional[str] = None


class InstructorCreate(InstructorBase):
    pass


class InstructorRead(InstructorBase):
    id_instructor: int


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    competencia: Optional[str] = None
    foto: Optional[str] = None