from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Novedad(SQLModel, table=True):
    __tablename__ = "novedades"

    id_novedad: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80, nullable=False)
    apellido: str = Field(max_length=80, nullable=False)
    correo: str = Field(max_length=120, nullable=False)
    ficha: str = Field(max_length=50, nullable=False)
    mensaje: str = Field(max_length=2000, nullable=False)
    leido: bool = Field(default=False, nullable=False)
    fecha: datetime = Field(default_factory=datetime.utcnow, nullable=False)