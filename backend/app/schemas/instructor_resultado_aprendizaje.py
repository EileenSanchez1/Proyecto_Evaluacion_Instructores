from typing import Optional
from sqlmodel import SQLModel
from app.schemas.resultado_aprendizaje import ResultadoAprendizajeRead


class InstructorResultadoAprendizajeBase(SQLModel):
    id_instructor: int
    id_resultado: int


class InstructorResultadoAprendizajeCreate(InstructorResultadoAprendizajeBase):
    pass


class InstructorResultadoAprendizajeRead(InstructorResultadoAprendizajeBase):
    id: int
    resultado_aprendizaje: Optional[ResultadoAprendizajeRead] = None
