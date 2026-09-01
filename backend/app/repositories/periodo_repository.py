from typing import List, Optional

from sqlmodel import Session, select

from app.models.periodo import Periodo
from app.schemas.periodo import PeriodoCreate, PeriodoUpdate


class PeriodoRepository:

    @staticmethod
    def crear(session: Session, periodo: PeriodoCreate) -> Periodo:
        db_periodo = Periodo(**periodo.model_dump())
        session.add(db_periodo)
        session.commit()
        session.refresh(db_periodo)
        return db_periodo

    @staticmethod
    def buscar(session: Session, periodo_id: int) -> Optional[Periodo]:
        return session.get(Periodo, periodo_id)

    @staticmethod
    def buscar_por_nombre(session: Session, nombre: str) -> Optional[Periodo]:
        statement = select(Periodo).where(Periodo.nombre == nombre)
        return session.exec(statement).first()

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Periodo]:
        statement = select(Periodo).offset(offset).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def listar_activos(session: Session) -> List[Periodo]:
        statement = select(Periodo).where(Periodo.estado == "Activo")
        return session.exec(statement).all()

    @staticmethod
    def actualizar(session: Session, periodo_id: int, periodo_update: PeriodoUpdate) -> Optional[Periodo]:
        db_periodo = session.get(Periodo, periodo_id)
        if not db_periodo:
            return None

        update_data = periodo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_periodo, key, value)

        session.add(db_periodo)
        session.commit()
        session.refresh(db_periodo)
        return db_periodo

    @staticmethod
    def eliminar(session: Session, periodo_id: int) -> bool:
        db_periodo = session.get(Periodo, periodo_id)
        if not db_periodo:
            return False
        session.delete(db_periodo)
        session.commit()
        return True
