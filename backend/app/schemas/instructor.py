from typing import List, Optional

from sqlmodel import SQLModel

from app.schemas.resultado_aprendizaje import ResultadoAprendizajeRead


class InstructorBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    foto: Optional[str] = None
    # PLANTA | CONTRATO
    planta_contrato: Optional[str] = None


class InstructorCreate(InstructorBase):
    resultados_aprendizaje: List[int] = []
    competencias: Optional[List[int]] = None


class InstructorRead(InstructorBase):
    id_instructor: int
    resultados_aprendizaje: List[ResultadoAprendizajeRead] = []
    activo: bool = True


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    foto: Optional[str] = None
    planta_contrato: Optional[str] = None
    resultados_aprendizaje: Optional[List[int]] = None
    competencias: Optional[List[int]] = None
