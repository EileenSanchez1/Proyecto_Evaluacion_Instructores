<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RespuestaBase(BaseModel):
    evaluacion_id: int
    pregunta_id: int
    aprendiz_id: int
    valor: str


class RespuestaCreate(RespuestaBase):
    pass


class RespuestaUpdate(BaseModel):
    evaluacion_id: Optional[int] = None
    pregunta_id: Optional[int] = None
    aprendiz_id: Optional[int] = None
    valor: Optional[str] = None


class RespuestaResponse(RespuestaBase):
    id: int
    fecha_respuesta: datetime

    class Config:
        from_attributes = True
=======
from typing import Optional

from sqlmodel import SQLModel


class RespuestaBase(SQLModel):
    respuesta: bool
    comentario: Optional[str] = None


class RespuestaCreate(RespuestaBase):
    id_evaluacion: int
    id_pregunta: int
    id_instructor: int


class RespuestaRead(RespuestaBase):
    id_respuesta: int
    id_evaluacion: int
    id_pregunta: int
    id_instructor: int


class RespuestaUpdate(SQLModel):
    respuesta: Optional[bool] = None
    comentario: Optional[str] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
