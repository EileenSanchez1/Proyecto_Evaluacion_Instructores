from typing import List, Optional

from sqlmodel import Session, select

from app.models.pregunta import Pregunta
from app.schemas.pregunta import PreguntaCreate, PreguntaUpdate


class PreguntaRepository:

    @staticmethod
    def crear(
        session: Session,
        pregunta: PreguntaCreate
    ) -> Pregunta:

        db_pregunta = Pregunta(
            **pregunta.model_dump()
        )

        session.add(db_pregunta)
        session.commit()
        session.refresh(db_pregunta)

        return db_pregunta

    @staticmethod
    def buscar(
        session: Session,
        pregunta_id: int
    ) -> Optional[Pregunta]:

        return session.get(
            Pregunta,
            pregunta_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Pregunta]:

        statement = (
            select(Pregunta)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_activas(
        session: Session
    ) -> List[Pregunta]:

        statement = (
            select(Pregunta)
            .where(Pregunta.estado == True)
            .order_by(Pregunta.orden)
        )

        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        pregunta_id: int,
        pregunta_update: PreguntaUpdate
    ) -> Optional[Pregunta]:

        db_pregunta = session.get(
            Pregunta,
            pregunta_id
        )

        if not db_pregunta:
            return None

        update_data = pregunta_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_pregunta, key, value)

        session.add(db_pregunta)
        session.commit()
        session.refresh(db_pregunta)

        return db_pregunta

    @staticmethod
    def eliminar(
        session: Session,
        pregunta_id: int
    ) -> bool:

        db_pregunta = session.get(
            Pregunta,
            pregunta_id
        )

        if not db_pregunta:
            return False

        session.delete(db_pregunta)
        session.commit()

        return True