from sqlmodel import Session
from typing import Optional
from app.models.evaluacion import Evaluacion
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.schemas.evaluacion import EvaluacionUpdate


class EvaluacionService:
    @staticmethod
    def cambiar_estado(session: Session, evaluacion_id: int, nuevo_estado: str) -> Optional[Evaluacion]:
        """
        Cambia el estado de una evaluación (ej: Pendiente -> Completada).
        """
        evaluacion = EvaluacionRepository.buscar(session, evaluacion_id)
        if not evaluacion:
            return None

        update_data = EvaluacionUpdate(estado=nuevo_estado)
        return EvaluacionRepository.actualizar(session, evaluacion_id, update_data)

    @staticmethod
    def crear_evaluacion(session: Session, id_aprendiz: int) -> Evaluacion:
        """
        Crea una nueva evaluación para un aprendiz.
        """
        from app.schemas.evaluacion import EvaluacionCreate
        nueva = EvaluacionCreate(id_aprendiz=id_aprendiz)
        return EvaluacionRepository.crear(session, nueva)