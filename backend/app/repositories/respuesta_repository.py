from typing import List, Optional

from sqlmodel import Session, select

from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate


class EvaluacionRepository:

    @staticmethod
    def crear(
        session: Session,
        evaluacion: EvaluacionCreate
    ) -> Evaluacion:
        """Crea una nueva evaluación."""

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
        """Busca una evaluación por su ID."""

        return session.get(
            Evaluacion,
            evaluacion_id
        )

    @staticmethod
    def actualizar(
        session: Session,
        evaluacion_id: int,
        evaluacion_update: EvaluacionUpdate
    ) -> Optional[Evaluacion]:
        """Actualiza una evaluación existente."""

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
    def eliminar(
        session: Session,
        evaluacion_id: int
    ) -> bool:
        """Elimina una evaluación por su ID."""

        db_evaluacion = session.get(
            Evaluacion,
            evaluacion_id
        )

        if not db_evaluacion:
            return False

        session.delete(db_evaluacion)
        session.commit()

        return True

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Evaluacion]:
        """Lista todas las evaluaciones."""

        statement = (
            select(Evaluacion)
            .order_by(Evaluacion.fecha.desc())
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_aprendiz(
        session: Session,
        aprendiz_id: int
    ) -> List[Evaluacion]:
        """Lista las evaluaciones de un aprendiz."""

        statement = select(Evaluacion).where(
            Evaluacion.id_aprendiz == aprendiz_id
        )

        return session.exec(statement).all()