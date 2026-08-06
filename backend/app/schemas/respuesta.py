from typing import Optional

from sqlmodel import SQLModel


class RespuestaCreate(SQLModel):
    respuesta: int
    comentario: Optional[str] = None
    id_evaluacion: int
    id_pregunta: int
    id_instructor: int


class RespuestaRead(SQLModel):
    id_respuesta: int
    respuesta: int
    comentario: Optional[str]
    id_evaluacion: int
    id_pregunta: int
    id_instructor: int


class RespuestaUpdate(SQLModel):
    respuesta: Optional[int] = None
    comentario: Optional[str] = None