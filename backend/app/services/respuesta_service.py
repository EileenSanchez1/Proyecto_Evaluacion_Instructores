from typing import List, Optional
from sqlmodel import Session
from app.models.respuesta import Respuesta
from app.schemas.respuesta import RespuestaCreate, RespuestaUpdate
from app.repositories.respuesta_repository import RespuestaRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.pregunta_repository import PreguntaRepository
from app.repositories.instructor_repository import InstructorRepository

class RespuestaService:
    @staticmethod
    def crear(session: Session, respuesta: RespuestaCreate) -> Respuesta:
        if not EvaluacionRepository.buscar(session, respuesta.id_evaluacion):
            raise ValueError("La evaluación no existe.")
        if not PreguntaRepository.buscar(session, respuesta.id_pregunta):
            raise ValueError("La pregunta no existe.")
        if not InstructorRepository.buscar(session, respuesta.id_instructor):
            raise ValueError("El instructor no existe.")
        if not (1 <= respuesta.respuesta <= 5):
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return RespuestaRepository.crear(session, respuesta)

    @staticmethod
    def buscar(session: Session, respuesta_id: int) -> Optional[Respuesta]:
        return RespuestaRepository.buscar(session, respuesta_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Respuesta]:
        return RespuestaRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_evaluacion(session: Session, id_evaluacion: int) -> List[Respuesta]:
        return RespuestaRepository.listar_por_evaluacion(session, id_evaluacion)

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[Respuesta]:
        return RespuestaRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def actualizar(session: Session, respuesta_id: int, respuesta_update: RespuestaUpdate) -> Optional[Respuesta]:
        if respuesta_update.respuesta is not None and not (1 <= respuesta_update.respuesta <= 5):
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return RespuestaRepository.actualizar(session, respuesta_id, respuesta_update)

    @staticmethod
    def eliminar(session: Session, respuesta_id: int) -> bool:
        return RespuestaRepository.eliminar(session, respuesta_id)

    @staticmethod
    def calcular_puntaje(session: Session, evaluacion_id: int) -> dict:
        respuestas = RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
        if not respuestas:
            return {"promedio": 0, "total_preguntas": 0, "escala": "1-5"}
        total = sum(r.respuesta for r in respuestas)
        promedio = total / len(respuestas)
        return {
            "promedio": round(promedio, 2),
            "total_preguntas": len(respuestas),
            "escala": "1-5",
            "maximo": 5
        }

    @staticmethod
    def calcular_puntaje_por_instructor(session: Session, evaluacion_id: int, instructor_id: int) -> dict:
        respuestas = [
            r for r in RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
            if r.id_instructor == instructor_id
        ]
        if not respuestas:
            return {"promedio": 0, "total_preguntas": 0, "escala": "1-5"}
        total = sum(r.respuesta for r in respuestas)
        promedio = total / len(respuestas)
        return {
            "promedio": round(promedio, 2),
            "total_preguntas": len(respuestas),
            "escala": "1-5",
            "maximo": 5
        }
