from typing import Optional

from sqlmodel import SQLModel


class FichaCreate(SQLModel):
    numero_ficha: str
    programa: str
    descripcion: Optional[str] = None


class FichaRead(SQLModel):
    id_ficha: int
    numero_ficha: str
    programa: str
    descripcion: Optional[str]


class FichaUpdate(SQLModel):
    numero_ficha: Optional[str] = None
    programa: Optional[str] = None
    descripcion: Optional[str] = None