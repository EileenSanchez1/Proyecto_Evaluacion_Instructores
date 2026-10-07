from typing import Optional
from sqlmodel import SQLModel

class FichaInstructorBase(SQLModel):
    id_ficha: int
    id_instructor: int
    id_periodo: int
    id_resultado: Optional[int] = None
    activo: bool = True

class FichaInstructorCreate(SQLModel):
    id_ficha: int
    id_instructor: int
    id_periodo: int
    id_resultado: Optional[int] = None

class FichaInstructorRead(FichaInstructorBase):
    id: int

class FichaInstructorUpdate(SQLModel):
    id_ficha: Optional[int] = None
    id_instructor: Optional[int] = None
    id_periodo: Optional[int] = None
    id_resultado: Optional[int] = None
    activo: Optional[bool] = None
