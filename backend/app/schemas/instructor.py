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
    # Lista de id_competencia a asignar al crear el instructor.
    competencias: List[int] = []


class InstructorRead(InstructorBase):
    id_instructor: int
    competencias: List[CompetenciaRead] = []


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    foto: Optional[str] = None
    # Si se envía, REEMPLAZA por completo el conjunto de competencias
    # del instructor. Si se omite (None), las competencias no se tocan.
    competencias: Optional[List[int]] = None
