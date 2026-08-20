<<<<<<< HEAD
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
=======
<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
=======
from __future__ import annotations

from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12


class Respuesta(SQLModel, table=True):
    __tablename__ = "respuestas"

<<<<<<< HEAD
=======
<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluacion_id: int = Field(foreign_key="evaluaciones.id", nullable=False)
    pregunta_id: int = Field(foreign_key="preguntas.id", nullable=False)
    aprendiz_id: int = Field(foreign_key="aprendices.id", nullable=False)
    valor: str = Field(nullable=False)  # "1-5", "sí", "no", o texto libre
    fecha_respuesta: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relaciones
    evaluacion: Optional["Evaluacion"] = Relationship(back_populates="respuestas")
    pregunta: Optional["Pregunta"] = Relationship(back_populates="respuestas")
    aprendiz: Optional["Aprendiz"] = Relationship(back_populates="respuestas")
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_respuesta: Optional[int] = Field(
        default=None,
        primary_key=True
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    respuesta: bool = Field(
        nullable=False
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    comentario: Optional[str] = Field(
        default=None,
        max_length=500
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_evaluacion: int = Field(
        foreign_key="evaluaciones.id_evaluacion",
        nullable=False
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_pregunta: int = Field(
        foreign_key="preguntas.id_pregunta",
        nullable=False
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_instructor: int = Field(
        foreign_key="instructores.id_instructor",
        nullable=False
    )

<<<<<<< HEAD
=======

    # =====================
    # Relaciones
    # =====================

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    evaluacion: "Evaluacion" = Relationship(
        back_populates="respuestas"
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    pregunta: "Pregunta" = Relationship(
        back_populates="respuestas"
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    instructor: "Instructor" = Relationship(
        back_populates="respuestas"
    )

<<<<<<< HEAD
    def __repr__(self):
        return f"<Respuesta {self.id_respuesta}>"
=======

    def __repr__(self):
        return f"<Respuesta {self.id_respuesta}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
