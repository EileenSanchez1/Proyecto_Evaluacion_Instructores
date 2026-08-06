from __future__ import annotations

from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class FichaInstructor(SQLModel, table=True):
    __tablename__ = "ficha_instructor"

    id: Optional[int] = Field(default=None, primary_key=True)

    id_ficha: int = Field(
        foreign_key="fichas.id_ficha"
    )

    id_instructor: int = Field(
        foreign_key="instructores.id_instructor"
    )

    ficha: "Ficha" = Relationship(
        back_populates="ficha_instructores"
    )

    instructor: "Instructor" = Relationship(
        back_populates="ficha_instructores"
    )