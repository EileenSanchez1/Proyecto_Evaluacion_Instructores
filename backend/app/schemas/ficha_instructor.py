from typing import Optional

from sqlmodel import SQLModel


class FichaInstructorCreate(SQLModel):
    id_ficha: int
    id_instructor: int


class FichaInstructorRead(SQLModel):
    id: int
    id_ficha: int
    id_instructor: int


class FichaInstructorUpdate(SQLModel):
    id_ficha: Optional[int] = None
    id_instructor: Optional[int] = None