from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index


class Respuesta(SQLModel, table=True):
    __tablename__ = "respuestas"

    __table_args__ = (
        Index("ix_respuestas_evaluacion", "id_evaluacion"),
        Index("ix_respuestas_instructor", "id_instructor"),
        Index("ix_respuestas_pregunta", "id_pregunta"),
    )

    id_respuesta: Optional[int] = Field(default=None, primary_key=True)
    id_evaluacion: int = Field(
        foreign_key="evaluaciones.id_evaluacion", nullable=False, index=True
    )
    id_pregunta: int = Field(
        foreign_key="preguntas.id_pregunta", nullable=False, index=True
    )
    id_instructor: int = Field(
        foreign_key="instructores.id_instructor", nullable=False, index=True
    )
    respuesta: int = Field(default=1, nullable=False)
    observaciones: Optional[str] = Field(default=None, max_length=500)

    evaluacion: "Evaluacion" = Relationship(back_populates="respuestas")
    pregunta: "Pregunta" = Relationship(back_populates="respuestas")
    instructor: "Instructor" = Relationship(back_populates="respuestas")

    def __repr__(self):
        return (
            f"<Respuesta eval={self.id_evaluacion} pregunta={self.id_pregunta} "
            f"valor={self.respuesta}>"
        )
