from typing import List, Optional
from sqlmodel import Session
from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import FichaInstructorCreate, FichaInstructorUpdate
from app.repositories.ficha_instructor_repository import FichaInstructorRepository
from app.repositories.ficha_repository import FichaRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.periodo_repository import PeriodoRepository

class FichaInstructorService:
    @staticmethod
    def crear(session: Session, ficha_instructor: FichaInstructorCreate) -> FichaInstructor:
        if not FichaRepository.buscar(session, ficha_instructor.id_ficha):
            raise ValueError("La ficha no existe.")
        if not InstructorRepository.buscar(session, ficha_instructor.id_instructor):
            raise ValueError("El instructor no existe.")
        if not PeriodoRepository.buscar(session, ficha_instructor.id_periodo):
            raise ValueError("El periodo no existe.")
        if FichaInstructorRepository.buscar_asignacion(session, ficha_instructor.id_ficha, ficha_instructor.id_instructor, ficha_instructor.id_periodo):
            raise ValueError("El instructor ya está asignado a esta ficha en el periodo seleccionado.")
        return FichaInstructorRepository.crear(session, ficha_instructor)

    @staticmethod
    def buscar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return FichaInstructorRepository.buscar(session, relacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_ficha(session: Session, id_ficha: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha(session, id_ficha)

    @staticmethod
    def listar_por_ficha_y_periodo(session: Session, id_ficha: int, id_periodo: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha_y_periodo(session, id_ficha, id_periodo)

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def actualizar(session: Session, relacion_id: int, update: FichaInstructorUpdate) -> Optional[FichaInstructor]:
        relacion = FichaInstructorRepository.buscar(session, relacion_id)
        if not relacion: return None
        id_ficha = update.id_ficha if update.id_ficha is not None else relacion.id_ficha
        id_instructor = update.id_instructor if update.id_instructor is not None else relacion.id_instructor
        id_periodo = update.id_periodo if update.id_periodo is not None else relacion.id_periodo
        if not FichaRepository.buscar(session, id_ficha): raise ValueError("La ficha no existe.")
        if not InstructorRepository.buscar(session, id_instructor): raise ValueError("El instructor no existe.")
        if not PeriodoRepository.buscar(session, id_periodo): raise ValueError("El periodo no existe.")
        ex = FichaInstructorRepository.buscar_asignacion(session, id_ficha, id_instructor, id_periodo)
        if ex and ex.id != relacion_id:
            raise ValueError("El instructor ya está asignado a esta ficha en el periodo seleccionado.")
        return FichaInstructorRepository.actualizar(session, relacion_id, update)

    @staticmethod
    def eliminar(session: Session, relacion_id: int) -> bool:
        return FichaInstructorRepository.eliminar(session, relacion_id)
