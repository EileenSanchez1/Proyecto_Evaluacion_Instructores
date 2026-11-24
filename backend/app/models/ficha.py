from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.aprendiz import Aprendiz
    from app.models.ficha_instructor import FichaInstructor


class Ficha(SQLModel, table=True):
    __tablename__ = "fichas"

    id_ficha: Optional[int] = Field(default=None, primary_key=True)
    numero_ficha: str = Field(unique=True, index=True, nullable=False, max_length=20)
    programa: str = Field(nullable=False, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)

    aprendices: list["Aprendiz"] = Relationship(back_populates="ficha")
    ficha_instructores: list["FichaInstructor"] = Relationship(back_populates="ficha")

    def __repr__(self):
        return f"<Ficha {self.numero_ficha}>"
