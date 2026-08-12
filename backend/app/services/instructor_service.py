from sqlmodel import Session
from typing import List, Optional
from app.models.instructor import Instructor
from app.repositories.instructor_repository import InstructorRepository


class InstructorService:
    @staticmethod
    def listar_instructores(session: Session, offset: int = 0, limit: int = 100) -> List[Instructor]:
        return InstructorRepository.listar(session, offset, limit)

    @staticmethod
    def obtener_instructor(session: Session, instructor_id: int) -> Optional[Instructor]:
        return InstructorRepository.buscar(session, instructor_id)