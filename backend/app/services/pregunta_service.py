from sqlmodel import Session
from typing import List
from app.models.pregunta import Pregunta
from app.repositories.pregunta_repository import PreguntaRepository


class PreguntaService:
    @staticmethod
    def listar_preguntas_activas(session: Session) -> List[Pregunta]:
        return PreguntaRepository.listar_activas(session)

    @staticmethod
    def listar_todas(session: Session, offset: int = 0, limit: int = 100) -> List[Pregunta]:
        return PreguntaRepository.listar(session, offset, limit)