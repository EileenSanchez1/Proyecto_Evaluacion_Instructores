from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Aprendiz(SQLModel, table=True):
    __tablename__ = "aprendices"

    id_aprendiz: Optional[int] = Field(default=None, primary_key=True)

    nombre: str = Field(max_length=80)

    apellido: str = Field(max_length=80)

    correo: str = Field(
        max_length=120,
        unique=True
    )

    contrasena: str = Field(max_length=255)

    id_ficha: int = Field(
        foreign_key="fichas.id_ficha"
    )

    # Relaciones
    ficha: "Ficha" = Relationship(
        back_populates="aprendices"
    )

    evaluaciones: List["Evaluacion"] = Relationship(
        back_populates="aprendiz"
    )