from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class EvaluacionBase(SQLModel):
    id_aprendiz: int
    id_periodo: int
    id_instructor: int
    estado: str = "Pendiente"

class EvaluacionCreate(EvaluacionBase):
    pass

class EvaluacionRead(SQLModel):
    id_evaluacion: int
    id_aprendiz: int
    id_periodo: int
    id_instructor: int
    estado: str
    fecha: datetime

class EvaluacionUpdate(SQLModel):
    estado: Optional[str] = None
