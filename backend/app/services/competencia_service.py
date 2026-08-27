from typing import List, Optional
from sqlmodel import Session

from app.models.competencia import Competencia
from app.schemas.competencia import CompetenciaCreate, CompetenciaUpdate
from app.repositories.competencia_repository import CompetenciaRepository


class CompetenciaService:

    @staticmethod
    def crear(
        session: Session,
        competencia: CompetenciaCreate
    ) -> Competencia:

        existente = CompetenciaRepository.buscar_por_nombre(
            session,
            competencia.nombre
        )

        if existente:
            raise ValueError(
                "Ya existe una competencia con ese nombre."
            )

        return CompetenciaRepository.crear(
            session,
            competencia
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Competencia]:

        return CompetenciaRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def buscar(
        session: Session,
        competencia_id: int
    ) -> Optional[Competencia]:

        return CompetenciaRepository.buscar(
            session,
            competencia_id
        )

    @staticmethod
    def actualizar(
        session: Session,
        competencia_id: int,
        competencia_update: CompetenciaUpdate
    ) -> Optional[Competencia]:

        competencia = CompetenciaRepository.buscar(
            session,
            competencia_id
        )

        if not competencia:
            return None

        if competencia_update.nombre:

            existente = CompetenciaRepository.buscar_por_nombre(
                session,
                competencia_update.nombre
            )

            if (
                existente
                and existente.id_competencia != competencia_id
            ):
                raise ValueError(
                    "Ya existe otra competencia con ese nombre."
                )

        return CompetenciaRepository.actualizar(
            session,
            competencia_id,
            competencia_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        competencia_id: int
    ) -> bool:

        return CompetenciaRepository.eliminar(
            session,
            competencia_id
        )
