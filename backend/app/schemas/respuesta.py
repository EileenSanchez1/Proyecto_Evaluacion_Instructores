from typing import Optional
from sqlmodel import SQLModel

class RespuestaBase(SQLModel):
    id_evaluacion: int
    id_pregunta: int
    id_instructor: int
    respuesta: int  # 1-5
    observaciones: Optional[str] = None

class RespuestaCreate(RespuestaBase):
    pass

class RespuestaRead(RespuestaBase):
    id_respuesta: int

class RespuestaUpdate(SQLModel):
    respuesta: Optional[int] = None
    observaciones: Optional[str] = None
