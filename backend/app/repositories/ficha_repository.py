from typing import List, Optional

from sqlmodel import Session, select

from app.models.ficha import Ficha
from app.schemas.ficha import FichaCreate, FichaUpdate


class FichaRepository:

    @staticmethod
    def crear(
        session: Session,
        ficha: FichaCreate
    ) -> Ficha:

        db_ficha = Ficha(
            **ficha.model_dump()
        )

        session.add(db_ficha)
        session.commit()
        session.refresh(db_ficha)

        return db_ficha

    @staticmethod
    def buscar(
        session: Session,
        ficha_id: int
    ) -> Optional[Ficha]:

        return session.get(
            Ficha,
            ficha_id
        )

    @staticmethod
    def buscar_por_numero(
        session: Session,
        numero_ficha: str
    ) -> Optional[Ficha]:

        statement = select(Ficha).where(
            Ficha.numero_ficha == numero_ficha
        )

        return session.exec(statement).first()

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Ficha]:

        statement = (
            select(Ficha)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        ficha_id: int,
        ficha_update: FichaUpdate
    ) -> Optional[Ficha]:

        db_ficha = session.get(
            Ficha,
            ficha_id
        )

        if not db_ficha:
            return None

        update_data = ficha_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_ficha, key, value)

        session.add(db_ficha)
        session.commit()
        session.refresh(db_ficha)

        return db_ficha

    @staticmethod
    def eliminar(
        session: Session,
        ficha_id: int
    ) -> bool:

        db_ficha = session.get(
            Ficha,
            ficha_id
        )

        if not db_ficha:
            return False

        session.delete(db_ficha)
        session.commit()

        return True