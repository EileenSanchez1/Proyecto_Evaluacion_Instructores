from typing import List, Optional

from sqlmodel import Session

from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionUpdate
)

from app.repositories.evaluacion_repository import (
    EvaluacionRepository
)

from app.repositories.aprendiz_repository import (
    AprendizRepository
)


class EvaluacionService:

    @staticmethod
    def crear(
        session: Session,
        evaluacion: EvaluacionCreate
    ) -> Evaluacion:

        aprendiz = AprendizRepository.buscar(
            session,
            evaluacion.id_aprendiz
        )

        if not aprendiz:
            raise ValueError(
                "El aprendiz no existe."
            )

        return EvaluacionRepository.crear(
            session,
            evaluacion
        )

    @staticmethod
    def buscar(
        session: Session,
        evaluacion_id: int
    ) -> Optional[Evaluacion]:

        return EvaluacionRepository.buscar(
            session,
            evaluacion_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Evaluacion]:

        return EvaluacionRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def listar_por_aprendiz(
        session: Session,
        id_aprendiz: int
    ) -> List[Evaluacion]:

        return EvaluacionRepository.listar_por_aprendiz(
            session,
            id_aprendiz
        )

    @staticmethod
    def listar_pendientes(
        session: Session
    ) -> List[Evaluacion]:

        return EvaluacionRepository.listar_pendientes(
            session
        )

    @staticmethod
    def actualizar(
        session: Session,
        evaluacion_id: int,
        evaluacion_update: EvaluacionUpdate
    ) -> Optional[Evaluacion]:

        evaluacion = EvaluacionRepository.buscar(
            session,
            evaluacion_id
        )

        if not evaluacion:
            return None

        return EvaluacionRepository.actualizar(
            session,
            evaluacion_id,
            evaluacion_update
        )

    @staticmethod
    def cambiar_estado(
        session: Session,
        evaluacion_id: int,
        nuevo_estado: str
    ) -> Optional[Evaluacion]:

        estados_validos = [
            "Pendiente",
            "Evaluado"
        ]

        if nuevo_estado not in estados_validos:
            raise ValueError(
                "El estado debe ser 'Pendiente' o 'Evaluado'."
            )

        evaluacion = EvaluacionRepository.buscar(
            session,
            evaluacion_id
        )

        if not evaluacion:
            return None

        return EvaluacionRepository.actualizar_estado(
            session,
            evaluacion_id,
            nuevo_estado
        )

    @staticmethod
    def eliminar(
        session: Session,
        evaluacion_id: int
    ) -> bool:

        return EvaluacionRepository.eliminar(
            session,
            evaluacion_id
        )