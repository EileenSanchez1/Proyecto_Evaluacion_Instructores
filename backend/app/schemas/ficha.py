from typing import Optional

from sqlmodel import SQLModel


class FichaBase(SQLModel):
    numero_ficha: str
    programa: str
    descripcion: Optional[str] = None


class FichaCreate(FichaBase):
    pass


class FichaRead(FichaBase):
    id_ficha: int


class FichaUpdate(SQLModel):
    numero_ficha: Optional[str] = None
    programa: Optional[str] = None
    descripcion: Optional[str] = None