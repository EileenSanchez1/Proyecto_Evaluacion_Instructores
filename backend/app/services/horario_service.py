from typing import List, Optional
from sqlmodel import Session

from app.models.horario import Horario
from app.schemas.horario import HorarioCreate, HorarioUpdate
from app.repositories.horario_repository import HorarioRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.ficha_repository import FichaRepository


class HorarioService:

    @staticmethod
    def _validar_rango(hora_inicio, hora_fin) -> None:
        if hora_inicio >= hora_fin:
            raise ValueError(
                "La hora de inicio debe ser anterior a la hora de fin."
            )

    @staticmethod
    def crear(
        session: Session,
        horario: HorarioCreate
    ) -> Horario:

        if not InstructorRepository.buscar(session, horario.id_instructor):
            raise ValueError("El instructor no existe.")

        if not FichaRepository.buscar(session, horario.id_ficha):
            raise ValueError("La ficha no existe.")

        HorarioService._validar_rango(
            horario.hora_inicio,
            horario.hora_fin
        )

        cruces = HorarioRepository.buscar_cruces(
            session,
            horario.id_instructor,
            horario.dia,
            horario.hora_inicio,
            horario.hora_fin
        )

        if cruces:
            raise ValueError(
                "El instructor ya tiene un horario asignado que se "
                f"cruza con ese rango el día {horario.dia}."
            )

        return HorarioRepository.crear(session, horario)

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Horario]:

        return HorarioRepository.listar(session, offset, limit)

    @staticmethod
    def buscar(
        session: Session,
        horario_id: int
    ) -> Optional[Horario]:

        return HorarioRepository.buscar(session, horario_id)

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[Horario]:

        return HorarioRepository.listar_por_instructor(
            session,
            id_instructor
        )

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[Horario]:

        return HorarioRepository.listar_por_ficha(session, id_ficha)

    @staticmethod
    def actualizar(
        session: Session,
        horario_id: int,
        horario_update: HorarioUpdate
    ) -> Optional[Horario]:

        horario = HorarioRepository.buscar(session, horario_id)

        if not horario:
            return None

        id_instructor = (
            horario_update.id_instructor
            if horario_update.id_instructor is not None
            else horario.id_instructor
        )

        id_ficha = (
            horario_update.id_ficha
            if horario_update.id_ficha is not None
            else horario.id_ficha
        )

        dia = (
            horario_update.dia
            if horario_update.dia is not None
            else horario.dia
        )

        hora_inicio = (
            horario_update.hora_inicio
            if horario_update.hora_inicio is not None
            else horario.hora_inicio
        )

        hora_fin = (
            horario_update.hora_fin
            if horario_update.hora_fin is not None
            else horario.hora_fin
        )

        if not InstructorRepository.buscar(session, id_instructor):
            raise ValueError("El instructor no existe.")

        if not FichaRepository.buscar(session, id_ficha):
            raise ValueError("La ficha no existe.")

        HorarioService._validar_rango(hora_inicio, hora_fin)

        cruces = HorarioRepository.buscar_cruces(
            session,
            id_instructor,
            dia,
            hora_inicio,
            hora_fin,
            excluir_id=horario_id
        )

        if cruces:
            raise ValueError(
                "El instructor ya tiene un horario asignado que se "
                f"cruza con ese rango el día {dia}."
            )

        return HorarioRepository.actualizar(
            session,
            horario_id,
            horario_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        horario_id: int
    ) -> bool:

        return HorarioRepository.eliminar(session, horario_id)
