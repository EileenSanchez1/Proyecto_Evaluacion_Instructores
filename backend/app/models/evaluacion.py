from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Evaluacion(SQLModel, table=True):
    __tablename__ = "evaluaciones"

    id_evaluacion: Optional[int] = Field(default=None, primary_key=True)
    id_aprendiz: int = Field(foreign_key="aprendices.id_aprendiz", nullable=False)
    id_periodo: int = Field(foreign_key="periodos.id_periodo", nullable=False)
    id_instructor: int = Field(foreign_key="instructores.id_instructor", nullable=False)
    estado: str = Field(default="Pendiente", max_length=20, nullable=False)
    fecha: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    aprendiz: "Aprendiz" = Relationship(back_populates="evaluaciones")
    periodo: "Periodo" = Relationship(back_populates="evaluaciones")
    instructor: "Instructor" = Relationship(back_populates="evaluaciones")
    respuestas: list["Respuesta"] = Relationship(back_populates="evaluacion")

    def __repr__(self):
        return f"<Evaluacion aprendiz={self.id_aprendiz} instructor={self.id_instructor} estado={self.estado}>"
