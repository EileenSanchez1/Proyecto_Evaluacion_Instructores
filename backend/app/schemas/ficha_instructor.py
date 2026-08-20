<<<<<<< HEAD
=======
<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional


class FichaInstructorCreate(BaseModel):
    ficha_id: int
    instructor_id: int


class FichaInstructorResponse(FichaInstructorCreate):
    id: int

    class Config:
        from_attributes = True
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from typing import Optional

from sqlmodel import SQLModel


class FichaInstructorBase(SQLModel):
    id_ficha: int
    id_instructor: int


class FichaInstructorCreate(FichaInstructorBase):
    pass


class FichaInstructorRead(FichaInstructorBase):
    id: int


class FichaInstructorUpdate(SQLModel):
    id_ficha: Optional[int] = None
<<<<<<< HEAD
    id_instructor: Optional[int] = None
=======
    id_instructor: Optional[int] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
