from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Notificacion(SQLModel, table=True):
    __tablename__ = "notificaciones"

    id_notificacion: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    id_usuario: int = Field(
        foreign_key="usuarios.id_usuario",
        nullable=False,
        index=True
    )

    titulo: str = Field(
        max_length=120,
        nullable=False
    )

    mensaje: str = Field(
        max_length=500,
        nullable=False
    )

    tipo: str = Field(
        default="info",
        max_length=20,
        nullable=False
    )

    fecha: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )

    leida: bool = Field(
        default=False,
        nullable=False
    )

    def __repr__(self):
        return f"<Notificacion {self.titulo}>"
