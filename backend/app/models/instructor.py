from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Instructor(SQLModel, table=True):
    __tablename__ = "instructores"

    id_instructor: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nombre: str = Field(
        max_length=80,
        nullable=False
    )

    apellido: str = Field(
        max_length=80,
        nullable=False
    )

    correo: str = Field(
        max_length=120,
        unique=True,
        index=True,
        nullable=False
    )

    telefono: str = Field(
        max_length=20,
        nullable=False
    )

    competencia: str = Field(
        max_length=120,
        nullable=False
    )

    foto: Optional[str] = Field(
        default=None,
        max_length=255
    )


    # =====================
    # Relaciones
    # =====================

    ficha_instructores: List["FichaInstructor"] = Relationship(
        back_populates="instructor"
    )

    respuestas: List["Respuesta"] = Relationship(
        back_populates="instructor"
    )


    def __repr__(self):
        return f"<Instructor {self.nombre} {self.apellido}>"