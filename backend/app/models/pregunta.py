<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

=======
from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e

class Pregunta(SQLModel, table=True):
    __tablename__ = "preguntas"

<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    enunciado: str = Field(nullable=False)
    tipo_respuesta: str = Field(default="escala", nullable=False)  # escala, texto, si_no
    categoria: Optional[str] = Field(default=None)  # puntualidad, metodologia, etc.
    orden: int = Field(default=0, nullable=False)
    estado: str = Field(default="activa", nullable=False)

    # Relaciones
    respuestas: List["Respuesta"] = Relationship(back_populates="pregunta")
=======
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
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
