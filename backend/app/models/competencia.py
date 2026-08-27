from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Competencia(SQLModel, table=True):
    __tablename__ = "competencias"

    id_competencia: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nombre: str = Field(
        max_length=120,
        unique=True,
        index=True,
        nullable=False
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=255
    )

    estado: bool = Field(
        default=True,
        nullable=False
    )

    instructor_competencias: list["InstructorCompetencia"] = Relationship(
        back_populates="competencia"
    )

    def __repr__(self):
        return f"<Competencia {self.nombre}>"
