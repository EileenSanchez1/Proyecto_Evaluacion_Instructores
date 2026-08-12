<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

=======
from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e

class Instructor(SQLModel, table=True):
    __tablename__ = "instructores"

<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo_documento: str = Field(default="CC", nullable=False)
    numero_documento: str = Field(unique=True, nullable=False, index=True)
    nombre_completo: str = Field(nullable=False)
    competencia: Optional[str] = Field(default=None)
    dia: Optional[str] = Field(default=None)  # Miércoles, Lunes, etc.
    correo_electronico: Optional[str] = Field(default=None)
    imagen: Optional[str] = Field(default="default.png")
    estado: str = Field(default="activo", nullable=False)

    # Relaciones
    evaluaciones: List["Evaluacion"] = Relationship(back_populates="instructor")
    fichas: List["FichaInstructor"] = Relationship(back_populates="instructor")
=======
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
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
