<<<<<<< HEAD
=======
<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class EvaluacionBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    ficha_id: int
    instructor_id: int
    estado: str = "pendiente"


class EvaluacionCreate(EvaluacionBase):
    pass


class EvaluacionUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    ficha_id: Optional[int] = None
    instructor_id: Optional[int] = None
    estado: Optional[str] = None


class EvaluacionResponse(EvaluacionBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
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
<<<<<<< HEAD
    estado: Optional[str] = None
=======
    estado: Optional[str] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
