<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
from typing import Optional


class AprendizBase(BaseModel):
    tipo_documento: str = "CC"
    numero_documento: str
    nombre_completo: str
    correo_electronico: EmailStr
    telefono: Optional[str] = None
    ficha_id: int
    estado: str = "activo"


class AprendizCreate(AprendizBase):
    pass


class AprendizUpdate(BaseModel):
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    nombre_completo: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    telefono: Optional[str] = None
    ficha_id: Optional[int] = None
    estado: Optional[str] = None


class AprendizResponse(AprendizBase):
    id: int

    class Config:
        from_attributes = True
=======
from typing import Optional

from sqlmodel import SQLModel


class AprendizBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    id_ficha: int


class AprendizCreate(AprendizBase):
    contrasena: str


class AprendizRead(AprendizBase):
    id_aprendiz: int


class AprendizUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    id_ficha: Optional[int] = None
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
