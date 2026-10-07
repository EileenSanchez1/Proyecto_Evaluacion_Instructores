from typing import List, Optional

from sqlmodel import Session, select

from app.models.resultado_aprendizaje import ResultadoAprendizaje
from app.schemas.resultado_aprendizaje import (
    ResultadoAprendizajeCreate,
    ResultadoAprendizajeUpdate,
)


class ResultadoAprendizajeRepository:

    @staticmethod
    def crear(
        session: Session,
        data: ResultadoAprendizajeCreate
    ) -> ResultadoAprendizaje:
        db = ResultadoAprendizaje(**data.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def buscar(
        session: Session,
        id_resultado: int
    ) -> Optional[ResultadoAprendizaje]:
        return session.get(ResultadoAprendizaje, id_resultado)

    @staticmethod
    def buscar_por_nombre(
        session: Session,
        nombre: str
    ) -> Optional[ResultadoAprendizaje]:
        statement = select(ResultadoAprendizaje).where(
            ResultadoAprendizaje.nombre == nombre
        )
        return session.exec(statement).first()

    @staticmethod
    def buscar_por_codigo(
        session: Session,
        codigo: str
    ) -> Optional[ResultadoAprendizaje]:
        if not codigo:
            return None
        statement = select(ResultadoAprendizaje).where(
            ResultadoAprendizaje.codigo == codigo
        )
        return session.exec(statement).first()

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[ResultadoAprendizaje]:
        statement = (
            select(ResultadoAprendizaje)
            .offset(offset)
            .limit(limit)
        )
        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        id_resultado: int,
        data: ResultadoAprendizajeUpdate
    ) -> Optional[ResultadoAprendizaje]:
        db = session.get(ResultadoAprendizaje, id_resultado)
        if not db:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db, key, value)
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def eliminar(session: Session, id_resultado: int) -> bool:
        """Soft delete: desactiva el RA."""
        db = session.get(ResultadoAprendizaje, id_resultado)
        if not db:
            return False
        db.estado = False
        session.add(db)
        session.commit()
        return True

    @staticmethod
    def reactivar(session: Session, id_resultado: int) -> bool:
        db = session.get(ResultadoAprendizaje, id_resultado)
        if not db:
            return False
        db.estado = True
        session.add(db)
        session.commit()
        return True
