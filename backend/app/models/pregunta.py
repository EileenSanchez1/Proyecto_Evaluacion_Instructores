from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Pregunta(SQLModel, table=True):
    __tablename__ = "preguntas"

    id_pregunta: Optional[int] = Field(default=None, primary_key=True)

    descripcion: str = Field(max_length=300)

    orden: int

    estado: bool = True

    respuestas: List["Respuesta"] = Relationship(
        back_populates="pregunta"
    )