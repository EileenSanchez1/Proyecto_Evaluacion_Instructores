from sqlmodel import Session
from typing import List, Dict
from app.models.respuesta import Respuesta
from app.repositories.respuesta_repository import RespuestaRepository
from app.schemas.respuesta import RespuestaCreate


class RespuestaService:
    @staticmethod
    def guardar_respuestas(session: Session, respuestas: List[RespuestaCreate]) -> List[Respuesta]:
        """
        Guarda múltiples respuestas de una evaluación.
        Cada respuesta incluye: id_evaluacion, id_pregunta, id_instructor, respuesta (bool), comentario.
        """
        guardadas = []
        for respuesta_data in respuestas:
            respuesta = RespuestaRepository.crear(session, respuesta_data)
            guardadas.append(respuesta)
        return guardadas

    @staticmethod
    def calcular_puntaje(session: Session, evaluacion_id: int) -> Dict:
        """
        Calcula el puntaje de una evaluación.
        Regla de negocio: Sí (True) = 1 punto, No (False) = 0 puntos.
        Retorna un diccionario con total de preguntas, puntaje obtenido y promedio.
        """
        respuestas = RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
        if not respuestas:
            return {
                "total_preguntas": 0,
                "puntaje": 0,
                "promedio": 0.0
            }

        total_preguntas = len(respuestas)
        puntaje = sum(1 for r in respuestas if r.respuesta is True)
        promedio = puntaje / total_preguntas if total_preguntas > 0 else 0.0

        return {
            "total_preguntas": total_preguntas,
            "puntaje": puntaje,
            "promedio": round(promedio, 2)
        }

    @staticmethod
    def calcular_puntaje_por_instructor(session: Session, evaluacion_id: int, instructor_id: int) -> Dict:
        """
        Calcula el puntaje de un instructor específico dentro de una evaluación.
        Sí (True) = 1, No (False) = 0.
        """
        respuestas = RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
        respuestas_instructor = [r for r in respuestas if r.id_instructor == instructor_id]

        if not respuestas_instructor:
            return {
                "id_instructor": instructor_id,
                "total_preguntas": 0,
                "puntaje": 0,
                "promedio": 0.0
            }

        total = len(respuestas_instructor)
        puntaje = sum(1 for r in respuestas_instructor if r.respuesta is True)
        promedio = puntaje / total if total > 0 else 0.0

        return {
            "id_instructor": instructor_id,
            "total_preguntas": total,
            "puntaje": puntaje,
            "promedio": round(promedio, 2)
        }