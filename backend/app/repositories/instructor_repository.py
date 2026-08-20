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

        return session.get(
            Instructor,
            instructor_id
        )

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ) -> Optional[Instructor]:

        statement = select(Instructor).where(
            Instructor.correo == correo
        )

        return session.exec(statement).first()

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Instructor]:

        statement = (
            select(Instructor)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        instructor_id: int,
        instructor_update: InstructorUpdate
    ) -> Optional[Instructor]:

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

        db_instructor = session.get(
            Instructor,
            instructor_id
        )

        if not db_instructor:
            return False

        session.delete(db_instructor)
        session.commit()

        return True