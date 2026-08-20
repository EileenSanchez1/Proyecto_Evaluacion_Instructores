<<<<<<< HEAD
=======
<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

=======
from __future__ import annotations

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint

<<<<<<< HEAD
=======
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12

class FichaInstructor(SQLModel, table=True):
    __tablename__ = "ficha_instructor"

<<<<<<< HEAD
=======
<<<<<<< HEAD
    id: Optional[int] = Field(default=None, primary_key=True)
    ficha_id: int = Field(foreign_key="fichas.id", nullable=False)
    instructor_id: int = Field(foreign_key="instructores.id", nullable=False)

    # Relaciones
    ficha: Optional["Ficha"] = Relationship(back_populates="instructores")
    instructor: Optional["Instructor"] = Relationship(back_populates="fichas")
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    __table_args__ = (
        UniqueConstraint(
            "id_ficha",
            "id_instructor",
            name="uq_ficha_instructor"
        ),
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    id_ficha: int = Field(
        foreign_key="fichas.id_ficha",
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
    ficha: "Ficha" = Relationship(
        back_populates="ficha_instructores"
    )

<<<<<<< HEAD
=======

>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    instructor: "Instructor" = Relationship(
        back_populates="ficha_instructores"
    )

<<<<<<< HEAD
    def __repr__(self):
        return (
            f"<FichaInstructor "
            f"ficha={self.id_ficha} "
            f"instructor={self.id_instructor}>"
        )
=======

    def __repr__(self):
        return f"<FichaInstructor ficha={self.id_ficha} instructor={self.id_instructor}>"
>>>>>>> 03a304607976fa9f108fb7359474d2faa00b321e
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
