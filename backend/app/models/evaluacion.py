<<<<<<< HEAD
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
=======
<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
=======
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12


class Evaluacion(SQLModel, table=True):
    __tablename__ = "evaluaciones"

<<<<<<< HEAD
=======
<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(nullable=False)
    descripcion: Optional[str] = Field(default=None)
    fecha_inicio: date = Field(nullable=False)
    fecha_fin: date = Field(nullable=False)
    ficha_id: int = Field(foreign_key="fichas.id", nullable=False)
    instructor_id: int = Field(foreign_key="instructores.id", nullable=False)
    estado: str = Field(default="pendiente", nullable=False)  # pendiente, activa, cerrada
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relaciones
    ficha: Optional["Ficha"] = Relationship(back_populates="evaluaciones")
    instructor: Optional["Instructor"] = Relationship(back_populates="evaluaciones")
    respuestas: List["Respuesta"] = Relationship(back_populates="evaluacion")
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_evaluacion: Optional[int] = Field(
        default=None,
        primary_key=True
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    fecha: datetime = Field(
        default_factory=datetime.now,
        nullable=False
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    estado: str = Field(
        default="Pendiente",
        max_length=20,
        nullable=False
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_aprendiz: int = Field(
        foreign_key="aprendices.id_aprendiz",
        nullable=False
    )

<<<<<<< HEAD
=======

    # =====================
    # Relaciones
    # =====================

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    aprendiz: "Aprendiz" = Relationship(
        back_populates="evaluaciones"
    )

<<<<<<< HEAD
    respuestas: list["Respuesta"] = Relationship(
        back_populates="evaluacion"
    )

    def __repr__(self):
        return f"<Evaluacion {self.id_evaluacion} - {self.estado}>"
=======

    respuestas: List["Respuesta"] = Relationship(
        back_populates="evaluacion"
    )


    def __repr__(self):
        return f"<Evaluacion {self.id_evaluacion} - {self.estado}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
