from typing import List, Optional

from sqlmodel import Session, select

from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import (
    FichaInstructorCreate,
    FichaInstructorUpdate
)


class FichaInstructorRepository:

    @staticmethod
    def crear(
        session: Session,
        ficha_instructor: FichaInstructorCreate
    ) -> FichaInstructor:
        """Crea una asignación entre una ficha y un instructor."""

        db_ficha_instructor = FichaInstructor(
            **ficha_instructor.model_dump()
        )

        session.add(db_ficha_instructor)
        session.commit()
        session.refresh(db_ficha_instructor)

        return db_ficha_instructor

    @staticmethod
    def buscar(
        session: Session,
        ficha_instructor_id: int
    ) -> Optional[FichaInstructor]:
        """Busca una asignación por su ID."""

        return session.get(
            FichaInstructor,
            ficha_instructor_id
        )

    @staticmethod
    def buscar_asignacion(
        session: Session,
        id_ficha: int,
        id_instructor: int
    ) -> Optional[FichaInstructor]:
        """Busca si un instructor ya está asignado a una ficha."""

        statement = select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha,
            FichaInstructor.id_instructor == id_instructor
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        ficha_instructor_id: int,
        ficha_instructor_update: FichaInstructorUpdate
    ) -> Optional[FichaInstructor]:
        """Actualiza una asignación."""

        db_ficha_instructor = session.get(
            FichaInstructor,
            ficha_instructor_id
        )

        if not db_ficha_instructor:
            return None

        update_data = ficha_instructor_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_ficha_instructor, key, value)

        session.add(db_ficha_instructor)
        session.commit()
        session.refresh(db_ficha_instructor)

        return db_ficha_instructor

    @staticmethod
    def eliminar(
        session: Session,
        ficha_instructor_id: int
    ) -> bool:
        """Elimina una asignación."""

        db_ficha_instructor = session.get(
            FichaInstructor,
            ficha_instructor_id
        )

        if not db_ficha_instructor:
            return False

        session.delete(db_ficha_instructor)
        session.commit()

        return True

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[FichaInstructor]:
        """Lista todas las asignaciones."""

        statement = (
            select(FichaInstructor)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[FichaInstructor]:
        """Lista los instructores asignados a una ficha."""

        statement = select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[FichaInstructor]:
        """Lista las fichas asignadas a un instructor."""

        statement = select(FichaInstructor).where(
            FichaInstructor.id_instructor == id_instructor
        )

        return session.exec(statement).all()