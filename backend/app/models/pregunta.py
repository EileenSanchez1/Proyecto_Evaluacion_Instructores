from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Pregunta(SQLModel, table=True):
    __tablename__ = "preguntas"

    id_pregunta: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    descripcion: str = Field(
        max_length=300,
        nullable=False
    )

    orden: int = Field(
        nullable=False,
        index=True
    )

    estado: bool = Field(
        default=True,
        nullable=False
    )


    # =====================
    # Relaciones
    # =====================

    respuestas: List["Respuesta"] = Relationship(
        back_populates="pregunta"
    )


    def __repr__(self):
        return f"<Pregunta {self.orden}>"