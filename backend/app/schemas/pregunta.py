<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional


class PreguntaBase(BaseModel):
    enunciado: str
    tipo_respuesta: str = "escala"
    categoria: Optional[str] = None
    orden: int = 0
    estado: str = "activa"
=======
from typing import Optional

from sqlmodel import SQLModel


class PreguntaBase(SQLModel):
    descripcion: str
    orden: int
    estado: bool = True
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e


class PreguntaCreate(PreguntaBase):
    pass


<<<<<<< HEAD
class PreguntaUpdate(BaseModel):
    enunciado: Optional[str] = None
    tipo_respuesta: Optional[str] = None
    categoria: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[str] = None


class PreguntaResponse(PreguntaBase):
    id: int

    class Config:
        from_attributes = True
=======
class PreguntaRead(PreguntaBase):
    id_pregunta: int


class PreguntaUpdate(SQLModel):
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[bool] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
