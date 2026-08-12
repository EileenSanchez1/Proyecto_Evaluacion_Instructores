<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
=======
from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e


class Ficha(SQLModel, table=True):
    __tablename__ = "fichas"

<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_ficha: str = Field(index=True, nullable=False)
    programa: str = Field(nullable=False)
    nivel: str = Field(nullable=False)  # Técnico, Tecnólogo, Complementaria
    jornada: str = Field(nullable=False)  # Diurna, Mixta, Nocturna, Fin de semana
    fecha_inicio: date = Field(nullable=False)
    fecha_fin: date = Field(nullable=False)
    estado: str = Field(default="En ejecución", nullable=False)  # En ejecución, Finalizada, Suspendida, Cancelada
    numero_aprendices: int = Field(default=0, nullable=False)

    # Relaciones
    aprendices: List["Aprendiz"] = Relationship(back_populates="ficha")
    evaluaciones: List["Evaluacion"] = Relationship(back_populates="ficha")
    instructores: List["FichaInstructor"] = Relationship(back_populates="ficha")
=======
    id_ficha: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    numero_ficha: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=20
    )

    programa: str = Field(
        nullable=False,
        max_length=120
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=255
    )

    # =====================
    # Relaciones
    # =====================

    aprendices: List["Aprendiz"] = Relationship(
        back_populates="ficha"
    )

    ficha_instructores: List["FichaInstructor"] = Relationship(
        back_populates="ficha"
    )

    def __repr__(self):
        return f"<Ficha {self.numero_ficha}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
