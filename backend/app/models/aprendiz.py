from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Aprendiz(SQLModel, table=True):
    __tablename__ = "aprendices"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo_documento: str = Field(default="CC", nullable=False)
    numero_documento: str = Field(unique=True, nullable=False)
    nombre_completo: str = Field(nullable=False)
    correo_electronico: str = Field(nullable=False)
    telefono: Optional[str] = Field(default=None)
    ficha_id: int = Field(foreign_key="fichas.id", nullable=False)
    estado: str = Field(default="activo", nullable=False)

    # Relaciones
    ficha: Optional["Ficha"] = Relationship(back_populates="aprendices")
    respuestas: List["Respuesta"] = Relationship(back_populates="aprendiz")

    id_aprendiz: Optional[int] = Field(
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

    contrasena: str = Field(
        max_length=255,
        nullable=False
    )

    id_ficha: int = Field(
        foreign_key="fichas.id_ficha",
        nullable=False
    )


    # =====================
    # Relaciones
    # =====================

    ficha: "Ficha" = Relationship(
        back_populates="aprendices"
    )

    evaluaciones: List["Evaluacion"] = Relationship(
        back_populates="aprendiz"
    )


    def __repr__(self):
        return f"<Aprendiz {self.nombre} {self.apellido}>"
