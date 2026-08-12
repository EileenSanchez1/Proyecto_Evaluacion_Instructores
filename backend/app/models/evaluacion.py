<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
=======
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e


class Evaluacion(SQLModel, table=True):
    __tablename__ = "evaluaciones"

<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(nullable=False)
    descripcion: Optional[str] = Field(default=None)
    fecha_inicio: date = Field(nullable=False)
    fecha_fin: date = Field(nullable=False)
    ficha_id: int = Field(foreign_key="fichas.id", nullable=False)
    instructor_id: int = Field(foreign_key="instructores.id", nullable=False)
    estado: str = Field(default="pendiente", nullable=False)  # pendiente, activa, cerrada
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relaciones
    ficha: Optional["Ficha"] = Relationship(back_populates="evaluaciones")
    instructor: Optional["Instructor"] = Relationship(back_populates="evaluaciones")
    respuestas: List["Respuesta"] = Relationship(back_populates="evaluacion")
=======

    id_evaluacion: Optional[int] = Field(
        default=None,
        primary_key=True
    )


    fecha: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )


    estado: str = Field(
        default="Pendiente",
        max_length=20,
        nullable=False
    )


    id_aprendiz: int = Field(
        foreign_key="aprendices.id_aprendiz",
        nullable=False
    )


    # =====================
    # Relaciones
    # =====================

    aprendiz: "Aprendiz" = Relationship(
        back_populates="evaluaciones"
    )


    respuestas: List["Respuesta"] = Relationship(
        back_populates="evaluacion"
    )


    def __repr__(self):
        return f"<Evaluacion {self.id_evaluacion} - {self.estado}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
