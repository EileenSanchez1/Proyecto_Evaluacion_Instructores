from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


class FichaInstructor(SQLModel, table=True):
    __tablename__ = "ficha_instructor"

    __table_args__ = (
        UniqueConstraint(
            "id_ficha",
            "id_instructor",
            name="uq_ficha_instructor"
        ),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    id_ficha: int = Field(
        foreign_key="fichas.id_ficha",
        nullable=False
    )

    id_instructor: int = Field(
        foreign_key="instructores.id_instructor",
        nullable=False
    )

    ficha: "Ficha" = Relationship(
        back_populates="ficha_instructores"
    )

    instructor: "Instructor" = Relationship(
        back_populates="ficha_instructores"
    )

    def __repr__(self):
        return (
            f"<FichaInstructor "
            f"ficha={self.id_ficha} "
            f"instructor={self.id_instructor}>"
        )