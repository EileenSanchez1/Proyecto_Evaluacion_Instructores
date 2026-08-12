from typing import List, Optional

from sqlmodel import Session, select

from app.models.instructor import Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate


class InstructorRepository:

    @staticmethod
    def crear(
        session: Session,
        instructor: InstructorCreate
    ) -> Instructor:
        """Crea un nuevo instructor."""

        db_instructor = Instructor(
            **instructor.model_dump()
        )

        session.add(db_instructor)
        session.commit()
        session.refresh(db_instructor)

        return db_instructor

    @staticmethod
    def buscar(
        session: Session,
        instructor_id: int
    ) -> Optional[Instructor]:
        """Busca un instructor por su ID."""

        return session.get(
            Instructor,
            instructor_id
        )

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ) -> Optional[Instructor]:
        """Busca un instructor por su correo."""

        statement = select(Instructor).where(
            Instructor.correo == correo
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        instructor_id: int,
        instructor_update: InstructorUpdate
    ) -> Optional[Instructor]:
        """Actualiza un instructor existente."""

        db_instructor = session.get(
            Instructor,
            instructor_id
        )

        if not db_instructor:
            return None

        update_data = instructor_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_instructor, key, value)

        session.add(db_instructor)
        session.commit()
        session.refresh(db_instructor)

        return db_instructor

    @staticmethod
    def eliminar(
        session: Session,
        instructor_id: int
    ) -> bool:
        """Elimina un instructor por su ID."""

        db_instructor = session.get(
            Instructor,
            instructor_id
        )

        if not db_instructor:
            return False

        session.delete(db_instructor)
        session.commit()

        return True

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Instructor]:
        """Lista los instructores."""

        statement = (
            select(Instructor)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()