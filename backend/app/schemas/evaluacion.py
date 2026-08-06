from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class EvaluacionCreate(SQLModel):
    id_aprendiz: int


class EvaluacionRead(SQLModel):
    id_evaluacion: int
    fecha: datetime
    estado: str
    id_aprendiz: int


class EvaluacionUpdate(SQLModel):
    estado: Optional[str] = None