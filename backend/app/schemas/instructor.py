<<<<<<< HEAD
=======
<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
from typing import Optional


class InstructorBase(BaseModel):
    tipo_documento: str = "CC"
    numero_documento: str
    nombre_completo: str
    competencia: Optional[str] = None
    dia: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    imagen: Optional[str] = "default.png"
    estado: str = "activo"
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from typing import Optional

from sqlmodel import SQLModel


class InstructorBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    telefono: str
    competencia: str
    foto: Optional[str] = None
<<<<<<< HEAD
=======
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12


class InstructorCreate(InstructorBase):
    pass


<<<<<<< HEAD
=======
<<<<<<< HEAD
class InstructorUpdate(BaseModel):
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    nombre_completo: Optional[str] = None
    competencia: Optional[str] = None
    dia: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    imagen: Optional[str] = None
    estado: Optional[str] = None


class InstructorResponse(InstructorBase):
    id: int

    class Config:
        from_attributes = True
=======
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
class InstructorRead(InstructorBase):
    id_instructor: int


class InstructorUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    competencia: Optional[str] = None
<<<<<<< HEAD
    foto: Optional[str] = None
=======
    foto: Optional[str] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
