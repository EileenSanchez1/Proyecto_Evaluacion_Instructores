from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NovedadCreate(BaseModel):
    nombre: str
    apellido: str
    correo: str
    ficha: str
    mensaje: str

class NovedadRead(BaseModel):
    id_novedad: int
    nombre: str
    apellido: str
    correo: str
    ficha: str
    mensaje: str
    leido: bool
    fecha: datetime

    class Config:
        from_attributes = True

class NovedadUpdate(BaseModel):
    leido: Optional[bool] = None