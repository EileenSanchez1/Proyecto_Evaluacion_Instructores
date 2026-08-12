from sqlmodel import Session
from typing import Tuple
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.respuesta_repository import RespuestaRepository


class AprendizService:
    @staticmethod
    def validar_no_evaluar_dos_veces(session: Session, aprendiz_id: int) -> Tuple[bool, str]:
        """
        Verifica que el aprendiz no haya respondido ninguna evaluación anterior.
        Si ya tiene respuestas, no puede evaluar de nuevo.
        Retorna: (puede_evaluar, mensaje)
        """
        aprendiz = AprendizRepository.buscar(session, aprendiz_id)
        if not aprendiz:
            return False, "Aprendiz no encontrado"

        evaluaciones = EvaluacionRepository.listar_por_aprendiz(session, aprendiz_id)
        for evaluacion in evaluaciones:
            if RespuestaRepository.ya_respondio(session, evaluacion.id_evaluacion):
                return False, "El aprendiz ya realizó la evaluación. No puede evaluar dos veces."

        return True, "El aprendiz puede evaluar"