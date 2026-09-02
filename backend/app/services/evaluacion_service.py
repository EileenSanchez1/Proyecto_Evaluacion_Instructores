from typing import List, Optional
from sqlmodel import Session
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.periodo_repository import PeriodoRepository

class EvaluacionService:
    @staticmethod
    def crear(session: Session, evaluacion: EvaluacionCreate) -> Evaluacion:
        if not AprendizRepository.buscar(session, evaluacion.id_aprendiz):
            raise ValueError("El aprendiz no existe.")
        if not InstructorRepository.buscar(session, evaluacion.id_instructor):
            raise ValueError("El instructor no existe.")
        if not PeriodoRepository.buscar(session, evaluacion.id_periodo):
            raise ValueError("El periodo no existe.")
        existente = EvaluacionRepository.buscar_por_aprendiz_instructor_periodo(
            session, evaluacion.id_aprendiz, evaluacion.id_instructor, evaluacion.id_periodo
        )
        if existente:
            raise ValueError("El aprendiz ya evaluó a este instructor en este periodo.")
        return EvaluacionRepository.crear(session, evaluacion)

    @staticmethod
    def buscar(session: Session, evaluacion_id: int) -> Optional[Evaluacion]:
        return EvaluacionRepository.buscar(session, evaluacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Evaluacion]:
        return EvaluacionRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_aprendiz(session: Session, id_aprendiz: int) -> List[Evaluacion]:
        return EvaluacionRepository.listar_por_aprendiz(session, id_aprendiz)

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[Evaluacion]:
        return EvaluacionRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def buscar_por_aprendiz_instructor_periodo(session: Session, id_aprendiz: int, id_instructor: int, id_periodo: int) -> Optional[Evaluacion]:
        return EvaluacionRepository.buscar_por_aprendiz_instructor_periodo(session, id_aprendiz, id_instructor, id_periodo)

    @staticmethod
    def actualizar(session: Session, evaluacion_id: int, evaluacion_update: EvaluacionUpdate) -> Optional[Evaluacion]:
        return EvaluacionRepository.actualizar(session, evaluacion_id, evaluacion_update)

    @staticmethod
    def actualizar_estado(session: Session, evaluacion_id: int, estado: str) -> Optional[Evaluacion]:
        return EvaluacionRepository.actualizar_estado(session, evaluacion_id, estado)

    @staticmethod
    def eliminar(session: Session, evaluacion_id: int) -> bool:
        return EvaluacionRepository.eliminar(session, evaluacion_id)
