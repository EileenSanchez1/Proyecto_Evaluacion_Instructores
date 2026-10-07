from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class ResultadoAprendizaje(SQLModel, table=True):
    """Resultado de Aprendizaje (RA) — reemplaza Competencia.

    Ejemplo del horario SENA:
      codigo: 220501-04
      nombre: CODIFICAR EL SOFTWARE DE ACUERDO CON EL DISEÑO ESTABLECIDO.
    """
    __tablename__ = "resultados_aprendizaje"

    id_resultado: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    codigo: Optional[str] = Field(
        default=None,
        max_length=30,
        index=True,
        description="Código del RA, ej. 220501-04"
    )

    nombre: str = Field(
        max_length=255,
        unique=True,
        index=True,
        nullable=False
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500
    )

    estado: bool = Field(
        default=True,
        nullable=False
    )

    instructor_resultados: list["InstructorResultadoAprendizaje"] = Relationship(
        back_populates="resultado_aprendizaje"
    )

    horarios: list["Horario"] = Relationship(
        back_populates="resultado_aprendizaje"
    )

    def __repr__(self):
        return f"<ResultadoAprendizaje {self.codigo or ''} {self.nombre}>"
