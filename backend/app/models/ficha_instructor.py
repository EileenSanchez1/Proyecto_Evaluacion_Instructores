from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Column, Boolean

class FichaInstructor(SQLModel, table=True):
    __tablename__ = "ficha_instructor"

    __table_args__ = (
        UniqueConstraint("id_ficha", "id_instructor", "id_periodo", name="uq_ficha_instructor_periodo"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    id_ficha: int = Field(foreign_key="fichas.id_ficha", nullable=False)
    id_instructor: int = Field(foreign_key="instructores.id_instructor", nullable=False)
    id_periodo: int = Field(foreign_key="periodos.id_periodo", nullable=False)
    # Resultado de aprendizaje que el instructor dicta en esta ficha/periodo (1 por trimestre)
    id_resultado: Optional[int] = Field(
        default=None,
        foreign_key="resultados_aprendizaje.id_resultado",
        nullable=True,
        index=True,
    )
    # Soft-delete: False = desactivado de esta ficha/periodo (no se muestra a aprendices)
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default="true"))

    ficha: "Ficha" = Relationship(back_populates="ficha_instructores")
    instructor: "Instructor" = Relationship(back_populates="ficha_instructores")
    periodo: "Periodo" = Relationship(back_populates="ficha_instructores")
    resultado_aprendizaje: Optional["ResultadoAprendizaje"] = Relationship()

    def __repr__(self):
        return (
            f"<FichaInstructor ficha={self.id_ficha} instructor={self.id_instructor} "
            f"periodo={self.id_periodo} resultado={self.id_resultado} activo={self.activo}>"
        )
