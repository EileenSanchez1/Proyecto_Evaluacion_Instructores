from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate


class EvaluacionRepository:

    @staticmethod
    def crear(session: Session, evaluacion: EvaluacionCreate) -> Evaluacion:
        """Crea una nueva evaluación en la base de datos."""
        db_evaluacion = Evaluacion(**evaluacion.model_dump())
        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)
        return db_evaluacion

    @staticmethod
    def buscar(session: Session, evaluacion_id: int) -> Optional[Evaluacion]:
        """Busca una evaluación por su ID."""
        return session.get(Evaluacion, evaluacion_id)

    @staticmethod
    def actualizar(session: Session, evaluacion_id: int, evaluacion_update: EvaluacionUpdate) -> Optional[Evaluacion]:
        """Actualiza una evaluación existente."""
        db_evaluacion = session.get(Evaluacion, evaluacion_id)
        if not db_evaluacion:
            return None

        update_data = evaluacion_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_evaluacion, key, value)

        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)
        return db_evaluacion

    @staticmethod
    def eliminar(session: Session, evaluacion_id: int) -> bool:
        """Elimina una evaluación por su ID."""
        db_evaluacion = session.get(Evaluacion, evaluacion_id)
        if not db_evaluacion:
            return False

        session.delete(db_evaluacion)
        session.commit()
        return True

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Evaluacion]:
        """Lista todas las evaluaciones con paginación."""
        statement = select(Evaluacion).offset(offset).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def listar_por_ficha(session: Session, ficha_id: int) -> List[Evaluacion]:
        """Lista las evaluaciones de una ficha específica."""
        statement = select(Evaluacion).where(Evaluacion.ficha_id == ficha_id)
        return session.exec(statement).all()

    @staticmethod
    def listar_por_instructor(session: Session, instructor_id: int) -> List[Evaluacion]:
        """Lista las evaluaciones de un instructor específico."""
        statement = select(Evaluacion).where(Evaluacion.instructor_id == instructor_id)
        return session.exec(statement).all()

    @staticmethod
    def listar_activas(session: Session) -> List[Evaluacion]:
        """Lista las evaluaciones activas (en curso)."""
        ahora = datetime.utcnow().date()
        statement = select(Evaluacion).where(
            Evaluacion.fecha_inicio <= ahora,
            Evaluacion.fecha_fin >= ahora,
            Evaluacion.estado == "activa"
        )
        return session.exec(statement).all()
