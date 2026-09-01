from typing import List, Optional

from sqlmodel import Session, select

from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionUpdate
)


class EvaluacionRepository:

    @staticmethod
    def crear(
        session: Session,
        evaluacion: EvaluacionCreate
    ) -> Evaluacion:

        db_evaluacion = Evaluacion(
            **evaluacion.model_dump()
        )

        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)

        return db_evaluacion

    @staticmethod
    def buscar(
        session: Session,
        evaluacion_id: int
    ) -> Optional[Evaluacion]:

        return session.get(
            Evaluacion,
            evaluacion_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Evaluacion]:

        statement = (
            select(Evaluacion)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_aprendiz(
        session: Session,
        id_aprendiz: int
    ) -> List[Evaluacion]:

        statement = select(Evaluacion).where(
            Evaluacion.id_aprendiz == id_aprendiz
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_pendientes(
        session: Session
    ) -> List[Evaluacion]:

        statement = select(Evaluacion).where(
            Evaluacion.estado == "Pendiente"
        )

        return session.exec(statement).all()

    @staticmethod
    def buscar_por_aprendiz_y_periodo(
        session: Session,
        id_aprendiz: int,
        id_periodo: int
    ) -> Optional[Evaluacion]:

        statement = select(Evaluacion).where(
            (Evaluacion.id_aprendiz == id_aprendiz) &
            (Evaluacion.id_periodo == id_periodo)
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        evaluacion_id: int,
        evaluacion_update: EvaluacionUpdate
    ) -> Optional[Evaluacion]:

        db_evaluacion = session.get(
            Evaluacion,
            evaluacion_id
        )

        if not db_evaluacion:
            return None

        update_data = evaluacion_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_evaluacion, key, value)

        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)

        return db_evaluacion

    @staticmethod
    def actualizar_estado(
        session: Session,
        evaluacion_id: int,
        estado: str
    ) -> Optional[Evaluacion]:

        db_evaluacion = session.get(
            Evaluacion,
            evaluacion_id
        )

        if not db_evaluacion:
            return None

        db_evaluacion.estado = estado

        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)

        return db_evaluacion

    @staticmethod
    def eliminar(
        session: Session,
        evaluacion_id: int
    ) -> bool:

        db_evaluacion = session.get(
            Evaluacion,
            evaluacion_id
        )

        if not db_evaluacion:
            return False

        session.delete(db_evaluacion)
        session.commit()

        return True
