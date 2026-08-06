from __future__ import annotations

from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Respuesta(SQLModel, table=True):
    __tablename__ = "respuestas"


    id_respuesta: Optional[int] = Field(
        default=None,
        primary_key=True
    )


    respuesta: bool = Field(
        nullable=False
    )


    comentario: Optional[str] = Field(
        default=None,
        max_length=500
    )


    id_evaluacion: int = Field(
        foreign_key="evaluaciones.id_evaluacion",
        nullable=False
    )


    id_pregunta: int = Field(
        foreign_key="preguntas.id_pregunta",
        nullable=False
    )


    id_instructor: int = Field(
        foreign_key="instructores.id_instructor",
        nullable=False
    )


    # =====================
    # Relaciones
    # =====================

    evaluacion: "Evaluacion" = Relationship(
        back_populates="respuestas"
    )


    pregunta: "Pregunta" = Relationship(
        back_populates="respuestas"
    )


    instructor: "Instructor" = Relationship(
        back_populates="respuestas"
    )


    def __repr__(self):
        return f"<Respuesta {self.id_respuesta}>"