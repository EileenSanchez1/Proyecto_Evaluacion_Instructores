<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

=======
from __future__ import annotations

from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint

>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e

class FichaInstructor(SQLModel, table=True):
    __tablename__ = "ficha_instructor"

<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    ficha_id: int = Field(foreign_key="fichas.id", nullable=False)
    instructor_id: int = Field(foreign_key="instructores.id", nullable=False)

    # Relaciones
    ficha: Optional["Ficha"] = Relationship(back_populates="instructores")
    instructor: Optional["Instructor"] = Relationship(back_populates="fichas")
=======

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


    # =====================
    # Relaciones
    # =====================

    ficha: "Ficha" = Relationship(
        back_populates="ficha_instructores"
    )


    instructor: "Instructor" = Relationship(
        back_populates="ficha_instructores"
    )


    def __repr__(self):
        return f"<FichaInstructor ficha={self.id_ficha} instructor={self.id_instructor}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
