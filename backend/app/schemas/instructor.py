from typing import List, Optional

from sqlmodel import SQLModel

from app.schemas.resultado_aprendizaje import ResultadoAprendizajeRead


class InstructorBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    foto: Optional[str] = None


class InstructorCreate(InstructorBase):
    # IDs de resultados de aprendizaje asignados al instructor
    resultados_aprendizaje: List[int] = []
    # Alias de compatibilidad (frontend antiguo puede enviar "competencias")
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
    resultados_aprendizaje: Optional[List[int]] = None
    competencias: Optional[List[int]] = None
