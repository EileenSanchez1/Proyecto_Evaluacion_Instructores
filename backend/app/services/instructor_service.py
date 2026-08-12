from typing import List, Optional

from sqlmodel import Session

from app.models.instructor import Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.repositories.instructor_repository import InstructorRepository


class InstructorService:

    @staticmethod
    def crear(
        session: Session,
        instructor: InstructorCreate
    ) -> Instructor:

        existente = InstructorRepository.buscar_por_correo(
            session,
            instructor.correo
        )

        if existente:
            raise ValueError(
                "Ya existe un instructor con ese correo."
            )

        return InstructorRepository.crear(
            session,
            instructor
        )

    @staticmethod
    def buscar(
        session: Session,
        instructor_id: int
    ) -> Optional[Instructor]:

        return InstructorRepository.buscar(
            session,
            instructor_id
        )

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ) -> Optional[Instructor]:

        return InstructorRepository.buscar_por_correo(
            session,
            correo
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Instructor]:

        return InstructorRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def actualizar(
        session: Session,
        instructor_id: int,
        instructor_update: InstructorUpdate
    ) -> Optional[Instructor]:

        instructor = InstructorRepository.buscar(
            session,
            instructor_id
        )

        if not instructor:
            return None

        if instructor_update.correo:

            existente = InstructorRepository.buscar_por_correo(
                session,
                instructor_update.correo
            )

            if (
                existente
                and existente.id_instructor != instructor_id
            ):
                raise ValueError(
                    "Ya existe otro instructor con ese correo."
                )

        return InstructorRepository.actualizar(
            session,
            instructor_id,
            instructor_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        instructor_id: int
    ) -> bool:

        return InstructorRepository.eliminar(
            session,
            instructor_id
        )