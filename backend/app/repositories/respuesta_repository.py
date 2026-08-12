from typing import List, Optional

from sqlmodel import Session, select

from app.models.respuesta import Respuesta
from app.schemas.respuesta import (
    RespuestaCreate,
    RespuestaUpdate
)


class RespuestaRepository:

    @staticmethod
    def crear(
        session: Session,
        respuesta: RespuestaCreate
    ) -> Respuesta:

        db_respuesta = Respuesta(
            **respuesta.model_dump()
        )

        session.add(db_respuesta)
        session.commit()
        session.refresh(db_respuesta)

        return db_respuesta

    @staticmethod
    def buscar(
        session: Session,
        respuesta_id: int
    ) -> Optional[Respuesta]:

        return session.get(
            Respuesta,
            respuesta_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Respuesta]:

        statement = (
            select(Respuesta)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_evaluacion(
        session: Session,
        id_evaluacion: int
    ) -> List[Respuesta]:

        statement = select(Respuesta).where(
            Respuesta.id_evaluacion == id_evaluacion
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_pregunta(
        session: Session,
        id_pregunta: int
    ) -> List[Respuesta]:

        statement = select(Respuesta).where(
            Respuesta.id_pregunta == id_pregunta
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[Respuesta]:

        statement = select(Respuesta).where(
            Respuesta.id_instructor == id_instructor
        )

        return session.exec(statement).all()

    @staticmethod
    def buscar_existente(
        session: Session,
        id_evaluacion: int,
        id_pregunta: int,
        id_instructor: int
    ) -> Optional[Respuesta]:

        statement = select(Respuesta).where(
            Respuesta.id_evaluacion == id_evaluacion,
            Respuesta.id_pregunta == id_pregunta,
            Respuesta.id_instructor == id_instructor
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        respuesta_id: int,
        respuesta_update: RespuestaUpdate
    ) -> Optional[Respuesta]:

        db_respuesta = session.get(
            Respuesta,
            respuesta_id
        )

        if not db_respuesta:
            return None

        update_data = respuesta_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_respuesta, key, value)

        session.add(db_respuesta)
        session.commit()
        session.refresh(db_respuesta)

        return db_respuesta

    @staticmethod
    def eliminar(
        session: Session,
        respuesta_id: int
    ) -> bool:

        db_respuesta = session.get(
            Respuesta,
            respuesta_id
        )

        if not db_respuesta:
            return False

        session.delete(db_respuesta)
        session.commit()

        return True