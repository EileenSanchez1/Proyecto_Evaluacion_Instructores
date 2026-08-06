from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Evaluacion(SQLModel, table=True):
    __tablename__ = "evaluaciones"


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