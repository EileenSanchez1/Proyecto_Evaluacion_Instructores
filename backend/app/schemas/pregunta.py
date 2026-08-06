from typing import Optional

from sqlmodel import SQLModel


class PreguntaCreate(SQLModel):
    descripcion: str
    orden: int
    estado: bool = True


class PreguntaRead(SQLModel):
    id_pregunta: int
    descripcion: str
    orden: int
    estado: bool


class PreguntaUpdate(SQLModel):
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[bool] = None