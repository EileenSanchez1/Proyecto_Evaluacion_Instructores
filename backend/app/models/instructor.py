from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Instructor(SQLModel, table=True):
    __tablename__ = "instructores"

    id_instructor: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80, nullable=False)
    apellido: str = Field(max_length=80, nullable=False)
    correo: str = Field(max_length=120, unique=True, index=True, nullable=False)
    telefono: str = Field(max_length=20, nullable=False)
    foto: Optional[str] = Field(default=None, max_length=255)
    id_usuario: Optional[int] = Field(default=None, foreign_key="usuarios.id_usuario", unique=True, nullable=True, index=True)

    ficha_instructores: list["FichaInstructor"] = Relationship(back_populates="instructor")
    respuestas: list["Respuesta"] = Relationship(back_populates="instructor")
    evaluaciones: list["Evaluacion"] = Relationship(back_populates="instructor")
    instructor_competencias: list["InstructorCompetencia"] = Relationship(back_populates="instructor")
    horarios: list["Horario"] = Relationship(back_populates="instructor")

    def __repr__(self):
        return f"<Instructor {self.nombre} {self.apellido}>"
