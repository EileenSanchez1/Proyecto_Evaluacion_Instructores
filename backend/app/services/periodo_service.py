from typing import List, Optional

from sqlmodel import Session

from app.models.periodo import Periodo
from app.schemas.periodo import PeriodoCreate, PeriodoUpdate
from app.repositories.periodo_repository import PeriodoRepository


class PeriodoService:

    @staticmethod
    def crear(session: Session, periodo: PeriodoCreate) -> Periodo:
        existente = PeriodoRepository.buscar_por_nombre(session, periodo.nombre)
        if existente:
            raise ValueError(f"Ya existe un periodo con el nombre '{periodo.nombre}'.")

        if periodo.fecha_fin <= periodo.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")

        return PeriodoRepository.crear(session, periodo)

    @staticmethod
    def buscar(session: Session, periodo_id: int) -> Optional[Periodo]:
        return PeriodoRepository.buscar(session, periodo_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Periodo]:
        return PeriodoRepository.listar(session, offset, limit)

    @staticmethod
    def listar_activos(session: Session) -> List[Periodo]:
        return PeriodoRepository.listar_activos(session)

    @staticmethod
    def actualizar(session: Session, periodo_id: int, periodo_update: PeriodoUpdate) -> Optional[Periodo]:
        periodo = PeriodoRepository.buscar(session, periodo_id)
        if not periodo:
            return None

        if periodo_update.nombre:
            existente = PeriodoRepository.buscar_por_nombre(session, periodo_update.nombre)
            if existente and existente.id_periodo != periodo_id:
                raise ValueError(f"Ya existe otro periodo con el nombre '{periodo_update.nombre}'.")

        if periodo_update.fecha_inicio and periodo_update.fecha_fin:
            if periodo_update.fecha_fin <= periodo_update.fecha_inicio:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")

        return PeriodoRepository.actualizar(session, periodo_id, periodo_update)

    @staticmethod
    def eliminar(session: Session, periodo_id: int) -> bool:
        return PeriodoRepository.eliminar(session, periodo_id)
