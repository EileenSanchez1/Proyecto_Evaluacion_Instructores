from typing import Optional

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

    respuestas: list["Respuesta"] = Relationship(
        back_populates="pregunta"
    )

    def __repr__(self):
        return f"<Pregunta {self.orden}>"