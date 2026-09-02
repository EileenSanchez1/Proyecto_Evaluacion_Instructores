from typing import Optional
from sqlmodel import SQLModel

class AprendizBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    id_ficha: int
    id_periodo: int

class AprendizCreate(SQLModel):
    nombre: str
    apellido: str
    correo: str
    contrasena: str
    id_ficha: int
    id_periodo: Optional[int] = None

class AprendizRead(SQLModel):
    id_aprendiz: int
    nombre: str
    apellido: str
    correo: str
    id_ficha: int
    id_periodo: int

class AprendizUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    id_ficha: Optional[int] = None
    id_periodo: Optional[int] = None
