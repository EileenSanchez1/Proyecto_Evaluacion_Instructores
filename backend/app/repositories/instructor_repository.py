<<<<<<< HEAD
from typing import List, Optional

from sqlmodel import Session, select

=======
from sqlmodel import Session, select
from typing import List, Optional
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from app.models.instructor import Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate


class InstructorRepository:

    @staticmethod
<<<<<<< HEAD
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

=======
    def crear(session: Session, instructor: InstructorCreate) -> Instructor:
        """Crea un nuevo instructor en la base de datos."""
        db_instructor = Instructor(**instructor.model_dump())
        session.add(db_instructor)
        session.commit()
        session.refresh(db_instructor)
        return db_instructor

    @staticmethod
    def buscar(session: Session, instructor_id: int) -> Optional[Instructor]:
        """Busca un instructor por su ID."""
        return session.get(Instructor, instructor_id)

    @staticmethod
    def buscar_por_documento(session: Session, numero_documento: str) -> Optional[Instructor]:
        """Busca un instructor por su número de documento."""
        statement = select(Instructor).where(Instructor.numero_documento == numero_documento)
        return session.exec(statement).first()

    @staticmethod
    def actualizar(session: Session, instructor_id: int, instructor_update: InstructorUpdate) -> Optional[Instructor]:
        """Actualiza un instructor existente."""
        db_instructor = session.get(Instructor, instructor_id)
        if not db_instructor:
            return None

        update_data = instructor_update.model_dump(exclude_unset=True)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        for key, value in update_data.items():
            setattr(db_instructor, key, value)

        session.add(db_instructor)
        session.commit()
        session.refresh(db_instructor)
<<<<<<< HEAD

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

=======
        return db_instructor

    @staticmethod
    def eliminar(session: Session, instructor_id: int) -> bool:
        """Elimina un instructor por su ID."""
        db_instructor = session.get(Instructor, instructor_id)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        if not db_instructor:
            return False

        session.delete(db_instructor)
        session.commit()
<<<<<<< HEAD

        return True
=======
        return True

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Instructor]:
        """Lista todos los instructores con paginación."""
        statement = select(Instructor).offset(offset).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def listar_activos(session: Session) -> List[Instructor]:
        """Lista solo los instructores activos."""
        statement = select(Instructor).where(Instructor.estado == "activo")
        return session.exec(statement).all()
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
