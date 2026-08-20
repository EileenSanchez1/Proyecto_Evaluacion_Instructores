<<<<<<< HEAD
from typing import List, Optional

from sqlmodel import Session, select

from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionUpdate
)
=======
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12


class EvaluacionRepository:

    @staticmethod
<<<<<<< HEAD
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

=======
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
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        for key, value in update_data.items():
            setattr(db_evaluacion, key, value)

        session.add(db_evaluacion)
        session.commit()
        session.refresh(db_evaluacion)
<<<<<<< HEAD

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

=======
        return db_evaluacion

    @staticmethod
    def eliminar(session: Session, evaluacion_id: int) -> bool:
        """Elimina una evaluación por su ID."""
        db_evaluacion = session.get(Evaluacion, evaluacion_id)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        if not db_evaluacion:
            return False

        session.delete(db_evaluacion)
        session.commit()
<<<<<<< HEAD

        return True
=======
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
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
