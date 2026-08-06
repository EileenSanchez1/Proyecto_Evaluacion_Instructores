from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class EvaluacionBase(SQLModel):
    estado: str = "Pendiente"


class EvaluacionCreate(SQLModel):
    id_aprendiz: int


class EvaluacionRead(EvaluacionBase):
    id_evaluacion: int
    fecha: datetime
    id_aprendiz: int


class EvaluacionUpdate(SQLModel):
    estado: Optional[str] = None