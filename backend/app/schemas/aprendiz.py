from typing import Optional
from sqlmodel import SQLModel


class AprendizBase(SQLModel):
    nombre: str
    apellido: str
    correo: str
    id_ficha: int
    id_periodo: int


class AprendizCreate(SQLModel):
    """
    Creación de aprendiz (admin/coordinador o carga masiva).
    Si no se envía contraseña, el sistema genera una temporal y la envía por correo.
    """
    nombre: str
    apellido: str
    correo: str
    contrasena: Optional[str] = None  # opcional: se genera si no viene
    id_ficha: int
    id_periodo: Optional[int] = None
    enviar_correo: bool = True  # estilo SGVA / cartero


class AprendizRead(SQLModel):
    id_aprendiz: int
    nombre: str
    apellido: str
    correo: str
    id_ficha: int
    id_periodo: int
    activo: bool = True


class AprendizUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    id_ficha: Optional[int] = None
    id_periodo: Optional[int] = None
