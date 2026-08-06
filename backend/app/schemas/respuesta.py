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