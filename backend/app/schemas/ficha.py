<<<<<<< HEAD
=======
<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional
from datetime import date


class FichaBase(BaseModel):
    numero_ficha: str
    programa: str
    nivel: str
    jornada: str
    fecha_inicio: date
    fecha_fin: date
    estado: str = "En ejecución"
    numero_aprendices: int = 0
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from typing import Optional

from sqlmodel import SQLModel


class FichaBase(SQLModel):
    numero_ficha: str
    programa: str
    descripcion: Optional[str] = None
<<<<<<< HEAD
=======
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12


class FichaCreate(FichaBase):
    pass


<<<<<<< HEAD
=======
<<<<<<< HEAD
class FichaUpdate(BaseModel):
    numero_ficha: Optional[str] = None
    programa: Optional[str] = None
    nivel: Optional[str] = None
    jornada: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    numero_aprendices: Optional[int] = None


class FichaResponse(FichaBase):
    id: int

    class Config:
        from_attributes = True
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
class FichaRead(FichaBase):
    id_ficha: int


class FichaUpdate(SQLModel):
    numero_ficha: Optional[str] = None
    programa: Optional[str] = None
<<<<<<< HEAD
    descripcion: Optional[str] = None
=======
    descripcion: Optional[str] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
