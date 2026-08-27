from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    id_rol: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nombre: str = Field(
        max_length=30,
        unique=True,
        index=True,
        nullable=False
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=255
    )

    activo: bool = Field(
        default=True,
        nullable=False
    )

    usuarios: list["Usuario"] = Relationship(
        back_populates="rol"
    )

    def __repr__(self):
        return f"<Rol {self.nombre}>"