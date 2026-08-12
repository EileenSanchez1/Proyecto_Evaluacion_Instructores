from typing import List, Optional

from sqlmodel import Session

from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import (
    FichaInstructorCreate,
    FichaInstructorUpdate
)

from app.repositories.ficha_instructor_repository import (
    FichaInstructorRepository
)

from app.repositories.ficha_repository import (
    FichaRepository
)

from app.repositories.instructor_repository import (
    InstructorRepository
)


class FichaInstructorService:

    @staticmethod
    def crear(
        session: Session,
        ficha_instructor: FichaInstructorCreate
    ) -> FichaInstructor:

        ficha = FichaRepository.buscar(
            session,
            ficha_instructor.id_ficha
        )

        if not ficha:
            raise ValueError(
                "La ficha no existe."
            )

        instructor = InstructorRepository.buscar(
            session,
            ficha_instructor.id_instructor
        )

        if not instructor:
            raise ValueError(
                "El instructor no existe."
            )

        existente = (
            FichaInstructorRepository.buscar_asignacion(
                session,
                ficha_instructor.id_ficha,
                ficha_instructor.id_instructor
            )
        )

        if existente:
            raise ValueError(
                "El instructor ya está asignado "
                "a esta ficha."
            )

        return FichaInstructorRepository.crear(
            session,
            ficha_instructor
        )

    @staticmethod
    def buscar(
        session: Session,
        relacion_id: int
    ) -> Optional[FichaInstructor]:

        return FichaInstructorRepository.buscar(
            session,
            relacion_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[FichaInstructor]:

        return FichaInstructorRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[FichaInstructor]:

        return FichaInstructorRepository.listar_por_ficha(
            session,
            id_ficha
        )

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[FichaInstructor]:

        return FichaInstructorRepository.listar_por_instructor(
            session,
            id_instructor
        )

    @staticmethod
    def actualizar(
        session: Session,
        relacion_id: int,
        ficha_instructor_update: FichaInstructorUpdate
    ) -> Optional[FichaInstructor]:

        relacion = FichaInstructorRepository.buscar(
            session,
            relacion_id
        )

        if not relacion:
            return None

        id_ficha = (
            ficha_instructor_update.id_ficha
            if ficha_instructor_update.id_ficha is not None
            else relacion.id_ficha
        )

        id_instructor = (
            ficha_instructor_update.id_instructor
            if ficha_instructor_update.id_instructor is not None
            else relacion.id_instructor
        )

        ficha = FichaRepository.buscar(
            session,
            id_ficha
        )

        if not ficha:
            raise ValueError(
                "La ficha no existe."
            )

        instructor = InstructorRepository.buscar(
            session,
            id_instructor
        )

        if not instructor:
            raise ValueError(
                "El instructor no existe."
            )

        existente = (
            FichaInstructorRepository.buscar_asignacion(
                session,
                id_ficha,
                id_instructor
            )
        )

        if (
            existente
            and existente.id != relacion_id
        ):
            raise ValueError(
                "El instructor ya está asignado "
                "a esta ficha."
            )

        return FichaInstructorRepository.actualizar(
            session,
            relacion_id,
            ficha_instructor_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        relacion_id: int
    ) -> bool:

        return FichaInstructorRepository.eliminar(
            session,
            relacion_id
        )