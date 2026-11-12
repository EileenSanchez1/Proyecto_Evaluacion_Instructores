from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index, Column, String


class Evaluacion(SQLModel, table=True):
    __tablename__ = "evaluaciones"

    __table_args__ = (
        # Índices para listados y anti-duplicado (rendimiento)
        Index("ix_evaluaciones_aprendiz", "id_aprendiz"),
        Index("ix_evaluaciones_instructor", "id_instructor"),
        Index("ix_evaluaciones_periodo", "id_periodo"),
        Index("ix_evaluaciones_estado", "estado"),
        Index(
            "ix_evaluaciones_aprendiz_instructor_periodo",
            "id_aprendiz",
            "id_instructor",
            "id_periodo",
        ),
    )

    id_evaluacion: Optional[int] = Field(default=None, primary_key=True)
    id_aprendiz: int = Field(foreign_key="aprendices.id_aprendiz", nullable=False, index=True)
    id_periodo: int = Field(foreign_key="periodos.id_periodo", nullable=False, index=True)
    id_instructor: int = Field(foreign_key="instructores.id_instructor", nullable=False, index=True)
    estado: str = Field(default="Pendiente", max_length=20, nullable=False, index=True)
    fecha: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    # Comentario general del aprendiz (aparte de observaciones por pregunta)
    observacion_general: Optional[str] = Field(default=None, max_length=1000)

    aprendiz: "Aprendiz" = Relationship(back_populates="evaluaciones")
    periodo: "Periodo" = Relationship(back_populates="evaluaciones")
    instructor: "Instructor" = Relationship(back_populates="evaluaciones")
    respuestas: list["Respuesta"] = Relationship(back_populates="evaluacion")

    def __repr__(self):
        return (
            f"<Evaluacion aprendiz={self.id_aprendiz} instructor={self.id_instructor} "
            f"estado={self.estado}>"
        )
