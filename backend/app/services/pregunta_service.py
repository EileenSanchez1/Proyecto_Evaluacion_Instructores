from typing import List, Optional

from sqlmodel import Session

from app.models.pregunta import Pregunta
from app.schemas.pregunta import PreguntaCreate, PreguntaUpdate
from app.repositories.pregunta_repository import PreguntaRepository


class PreguntaService:

    @staticmethod
    def crear(
        session: Session,
        pregunta: PreguntaCreate
    ) -> Pregunta:

        return PreguntaRepository.crear(
            session,
            pregunta
        )

    @staticmethod
    def buscar(
        session: Session,
        pregunta_id: int
    ) -> Optional[Pregunta]:

        return PreguntaRepository.buscar(
            session,
            pregunta_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Pregunta]:

        return PreguntaRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def listar_activas(
        session: Session
    ) -> List[Pregunta]:

        return PreguntaRepository.listar_activas(
            session
        )

    @staticmethod
    def actualizar(
        session: Session,
        pregunta_id: int,
        pregunta_update: PreguntaUpdate
    ) -> Optional[Pregunta]:

        pregunta = PreguntaRepository.buscar(
            session,
            pregunta_id
        )

        if not pregunta:
            return None

        return PreguntaRepository.actualizar(
            session,
            pregunta_id,
            pregunta_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        pregunta_id: int
    ) -> bool:

        return PreguntaRepository.eliminar(
            session,
            pregunta_id
        )