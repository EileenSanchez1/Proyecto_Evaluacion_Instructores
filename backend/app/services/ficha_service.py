from sqlmodel import Session
from typing import List
from app.repositories.ficha_repository import FichaRepository
from app.repositories.instructor_repository import InstructorRepository


class FichaService:
    @staticmethod
    def obtener_instructores_de_ficha(session: Session, ficha_id: int) -> List[dict]:
        """
        Retorna la lista de instructores asignados a una ficha específica.
        """
        ficha = FichaRepository.buscar(session, ficha_id)
        if not ficha:
            return []

        instructores = []
        for fi in ficha.ficha_instructores:
            instructor = InstructorRepository.buscar(session, fi.id_instructor)
            if instructor:
                instructores.append({
                    "id_instructor": instructor.id_instructor,
                    "nombre": instructor.nombre,
                    "apellido": instructor.apellido,
                    "correo": instructor.correo,
                    "telefono": instructor.telefono,
                    "competencia": instructor.competencia,
                    "foto": instructor.foto
                })
        return instructores