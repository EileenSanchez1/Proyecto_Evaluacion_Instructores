from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


class InstructorResultadoAprendizaje(SQLModel, table=True):
    """Asignación de Resultados de Aprendizaje a un instructor."""
    __tablename__ = "instructor_resultado_aprendizaje"

    __table_args__ = (
        UniqueConstraint(
            "id_instructor",
            "id_resultado",
            name="uq_instructor_resultado"
        ),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    id_instructor: int = Field(
        foreign_key="instructores.id_instructor",
        nullable=False
    )

    id_resultado: int = Field(
        foreign_key="resultados_aprendizaje.id_resultado",
        nullable=False
    )

    instructor: "Instructor" = Relationship(
        back_populates="instructor_resultados"
    )

    resultado_aprendizaje: "ResultadoAprendizaje" = Relationship(
        back_populates="instructor_resultados"
    )

    def __repr__(self):
        return (
            f"<InstructorResultadoAprendizaje "
            f"instructor={self.id_instructor} "
            f"resultado={self.id_resultado}>"
        )
