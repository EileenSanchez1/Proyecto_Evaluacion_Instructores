from datetime import time
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


DIAS_VALIDOS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]


class Horario(SQLModel, table=True):
    __tablename__ = "horarios"

    id_horario: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    id_instructor: int = Field(
        foreign_key="instructores.id_instructor",
        nullable=False,
        index=True
    )

    id_ficha: int = Field(
        foreign_key="fichas.id_ficha",
        nullable=False,
        index=True
    )

    dia: str = Field(
        max_length=15,
        nullable=False
    )

    hora_inicio: time = Field(
        nullable=False
    )

    hora_fin: time = Field(
        nullable=False
    )

    instructor: "Instructor" = Relationship(
        back_populates="horarios"
    )

    ficha: "Ficha" = Relationship(
        back_populates="horarios"
    )

    def __repr__(self):
        return (
            f"<Horario instructor={self.id_instructor} "
            f"{self.dia} {self.hora_inicio}-{self.hora_fin}>"
        )
