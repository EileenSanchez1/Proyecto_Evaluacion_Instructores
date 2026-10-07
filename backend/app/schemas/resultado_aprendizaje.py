from typing import Optional

from sqlmodel import SQLModel


class ResultadoAprendizajeBase(SQLModel):
    codigo: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    estado: bool = True


class ResultadoAprendizajeCreate(ResultadoAprendizajeBase):
    pass


class ResultadoAprendizajeRead(ResultadoAprendizajeBase):
    id_resultado: int


class ResultadoAprendizajeUpdate(SQLModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[bool] = None
