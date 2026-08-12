from typing import List, Optional

from sqlmodel import Session

from app.models.ficha import Ficha
from app.schemas.ficha import FichaCreate, FichaUpdate
from app.repositories.ficha_repository import FichaRepository


class FichaService:

    @staticmethod
    def crear(
        session: Session,
        ficha: FichaCreate
    ) -> Ficha:

        existente = FichaRepository.buscar_por_numero(
            session,
            ficha.numero_ficha
        )

        if existente:
            raise ValueError(
                "Ya existe una ficha con ese número."
            )

        return FichaRepository.crear(
            session,
            ficha
        )

    @staticmethod
    def buscar(
        session: Session,
        ficha_id: int
    ) -> Optional[Ficha]:

        return FichaRepository.buscar(
            session,
            ficha_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Ficha]:

        return FichaRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def actualizar(
        session: Session,
        ficha_id: int,
        ficha_update: FichaUpdate
    ) -> Optional[Ficha]:

        ficha = FichaRepository.buscar(
            session,
            ficha_id
        )

        if not ficha:
            return None

        if ficha_update.numero_ficha:

            existente = FichaRepository.buscar_por_numero(
                session,
                ficha_update.numero_ficha
            )

            if (
                existente
                and existente.id_ficha != ficha_id
            ):
                raise ValueError(
                    "Ya existe otra ficha con ese número."
                )

        return FichaRepository.actualizar(
            session,
            ficha_id,
            ficha_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        ficha_id: int
    ) -> bool:

        return FichaRepository.eliminar(
            session,
            ficha_id
        )