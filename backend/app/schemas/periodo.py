from datetime import date
from typing import Optional

from sqlmodel import SQLModel


class PeriodoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date
    estado: str = "Activo"


class PeriodoCreate(PeriodoBase):
    pass


class PeriodoRead(PeriodoBase):
    id_periodo: int


class PeriodoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
