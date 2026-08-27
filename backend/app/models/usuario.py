from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id_usuario: Optional[int] = Field(
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

    foto: Optional[str] = Field(
        default=None,
        max_length=500
    )

    id_rol: int = Field(
        foreign_key="roles.id_rol",
        nullable=False,
        index=True
    )

    activo: bool = Field(
        default=True,
        nullable=False
    )

    fecha_creacion: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )

    rol: "Rol" = Relationship(
        back_populates="usuarios"
    )

    def __repr__(self):
        return f"<Usuario {self.correo}>"