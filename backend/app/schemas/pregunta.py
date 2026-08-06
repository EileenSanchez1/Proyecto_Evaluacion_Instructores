from typing import Optional

from sqlmodel import SQLModel


class PreguntaBase(SQLModel):
    descripcion: str
    orden: int
    estado: bool = True


class PreguntaCreate(PreguntaBase):
    pass


class PreguntaRead(PreguntaBase):
    id_pregunta: int


class PreguntaUpdate(SQLModel):
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[bool] = None