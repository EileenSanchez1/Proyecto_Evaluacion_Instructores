from typing import List, Optional

from sqlmodel import SQLModel

from app.schemas.competencia import CompetenciaRead


class InstructorBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    foto: Optional[str] = None


class InstructorCreate(InstructorBase):
    competencias: List[int] = []


class InstructorRead(InstructorBase):
    id_instructor: int
    competencias: List[CompetenciaRead] = []
    activo: bool = True


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    foto: Optional[str] = None
    competencias: Optional[List[int]] = None
