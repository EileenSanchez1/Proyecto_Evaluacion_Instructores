from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


class InstructorCompetencia(SQLModel, table=True):
    __tablename__ = "instructor_competencia"

    __table_args__ = (
        UniqueConstraint(
            "id_instructor",
            "id_competencia",
            name="uq_instructor_competencia"
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

    id_competencia: int = Field(
        foreign_key="competencias.id_competencia",
        nullable=False
    )

    instructor: "Instructor" = Relationship(
        back_populates="instructor_competencias"
    )

    competencia: "Competencia" = Relationship(
        back_populates="instructor_competencias"
    )

    def __repr__(self):
        return (
            f"<InstructorCompetencia "
            f"instructor={self.id_instructor} "
            f"competencia={self.id_competencia}>"
        )
