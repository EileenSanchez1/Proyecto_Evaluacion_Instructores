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

        db_relacion = FichaInstructor(
            **ficha_instructor.model_dump()
        )

        session.add(db_relacion)
        session.commit()
        session.refresh(db_relacion)

        return db_relacion

    @staticmethod
    def buscar(
        session: Session,
        relacion_id: int
    ) -> Optional[FichaInstructor]:

        return session.get(
            FichaInstructor,
            relacion_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[FichaInstructor]:

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

        statement = select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[FichaInstructor]:

        statement = select(FichaInstructor).where(
            FichaInstructor.id_instructor == id_instructor
        )

        return session.exec(statement).all()

    @staticmethod
    def buscar_asignacion(
        session: Session,
        id_ficha: int,
        id_instructor: int
    ) -> Optional[FichaInstructor]:

        statement = select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha,
            FichaInstructor.id_instructor == id_instructor
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        relacion_id: int,
        ficha_instructor_update: FichaInstructorUpdate
    ) -> Optional[FichaInstructor]:

        db_relacion = session.get(
            FichaInstructor,
            relacion_id
        )

        if not db_relacion:
            return None

        update_data = ficha_instructor_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_relacion, key, value)

        session.add(db_relacion)
        session.commit()
        session.refresh(db_relacion)

        return db_relacion

    @staticmethod
    def eliminar(
        session: Session,
        relacion_id: int
    ) -> bool:

        db_relacion = session.get(
            FichaInstructor,
            relacion_id
        )

        if not db_relacion:
            return False

        session.delete(db_relacion)
        session.commit()

        return True