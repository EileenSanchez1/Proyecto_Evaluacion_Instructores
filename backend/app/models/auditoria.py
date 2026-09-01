from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Auditoria(SQLModel, table=True):
    __tablename__ = "auditoria"

    id_auditoria: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    id_usuario: Optional[int] = Field(
        default=None,
        foreign_key="usuarios.id_usuario",
        nullable=True
    )

    accion: str = Field(
        max_length=50,
        nullable=False
    )

    modulo: str = Field(
        max_length=50,
        nullable=False
    )

    descripcion: str = Field(
        max_length=500,
        nullable=False
    )

    fecha: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )

    ip_address: Optional[str] = Field(
        default=None,
        max_length=45
    )

    def __repr__(self):
        return f"<Auditoria {self.accion} {self.modulo}>"
