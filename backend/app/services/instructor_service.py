from typing import List, Optional
from sqlmodel import Session

from app.models.instructor import Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.competencia_repository import CompetenciaRepository
from app.repositories.instructor_competencia_repository import (
    InstructorCompetenciaRepository
)


class InstructorService:

    @staticmethod
    def _construir_read(instructor: Instructor) -> dict:
        """
        Arma el diccionario que espera InstructorRead, incluyendo
        las competencias asignadas (relación m2m).
        """

        return {
            "id_instructor": instructor.id_instructor,
            "nombre": instructor.nombre,
            "apellido": instructor.apellido,
            "correo": instructor.correo,
            "telefono": instructor.telefono,
            "foto": instructor.foto,
            "competencias": [
                {
                    "id_competencia": ic.competencia.id_competencia,
                    "nombre": ic.competencia.nombre,
                    "descripcion": ic.competencia.descripcion,
                    "estado": ic.competencia.estado,
                }
                for ic in instructor.instructor_competencias
            ],
        }

    @staticmethod
    def _validar_competencias(
        session: Session,
        ids_competencia: List[int]
    ) -> None:

        for id_competencia in ids_competencia:
            if not CompetenciaRepository.buscar(session, id_competencia):
                raise ValueError(
                    f"La competencia con id {id_competencia} no existe."
                )

    @staticmethod
    def _asignar_competencias(
        session: Session,
        id_instructor: int,
        ids_competencia: List[int]
    ) -> None:

        # Reemplaza el conjunto completo de competencias del instructor.
        InstructorCompetenciaRepository.eliminar_por_instructor(
            session,
            id_instructor
        )

        for id_competencia in ids_competencia:
            InstructorCompetenciaRepository.crear(
                session,
                id_instructor,
                id_competencia
            )

    @staticmethod
    def crear(
        session: Session,
        instructor: InstructorCreate
    ) -> dict:

        existente = InstructorRepository.buscar_por_correo(
            session,
            instructor.correo
        )

        if existente:
            raise ValueError(
                "Ya existe un instructor con ese correo."
            )

        InstructorService._validar_competencias(
            session,
            instructor.competencias
        )

        db_instructor = InstructorRepository.crear(
            session,
            instructor
        )

        if instructor.competencias:
            InstructorService._asignar_competencias(
                session,
                db_instructor.id_instructor,
                instructor.competencias
            )
            session.refresh(db_instructor)

        return InstructorService._construir_read(db_instructor)

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[dict]:

        instructores = InstructorRepository.listar(session, offset, limit)

        return [
            InstructorService._construir_read(i) for i in instructores
        ]

    @staticmethod
    def buscar(
        session: Session,
        instructor_id: int
    ) -> Optional[dict]:

        instructor = InstructorRepository.buscar(
            session,
            instructor_id
        )

        if not instructor:
            return None

        return InstructorService._construir_read(instructor)

    @staticmethod
    def actualizar(
        session: Session,
        instructor_id: int,
        instructor_update: InstructorUpdate
    ) -> Optional[dict]:

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

        if instructor_update.competencias is not None:
            InstructorService._validar_competencias(
                session,
                instructor_update.competencias
            )

        db_instructor = InstructorRepository.actualizar(
            session,
            instructor_id,
            instructor_update
        )

        if instructor_update.competencias is not None:
            InstructorService._asignar_competencias(
                session,
                instructor_id,
                instructor_update.competencias
            )
            session.refresh(db_instructor)

        return InstructorService._construir_read(db_instructor)

    @staticmethod
    def eliminar(
        session: Session,
        instructor_id: int
    ) -> bool:

        return InstructorRepository.eliminar(
            session,
            instructor_id
        )
