from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Periodo(SQLModel, table=True):
    __tablename__ = "periodos"

    id_periodo: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=20, unique=True, index=True, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    fecha_inicio: date = Field(nullable=False)
    fecha_fin: date = Field(nullable=False)
    estado: str = Field(default="Activo", max_length=20, nullable=False)

    evaluaciones: list["Evaluacion"] = Relationship(back_populates="periodo")
    aprendices: list["Aprendiz"] = Relationship(back_populates="periodo")
    ficha_instructores: list["FichaInstructor"] = Relationship(back_populates="periodo")

    def __repr__(self):
        return f"<Periodo {self.nombre}>"
