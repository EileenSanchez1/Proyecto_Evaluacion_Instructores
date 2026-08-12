from typing import List, Optional

from sqlmodel import Session, select

from app.models.ficha import Ficha
from app.schemas.ficha import FichaCreate, FichaUpdate


class FichaRepository:

    @staticmethod
    def crear(session: Session, ficha: FichaCreate) -> Ficha:
        """Crea una nueva ficha."""
        db_ficha = Ficha(**ficha.model_dump())

        session.add(db_ficha)
        session.commit()
        session.refresh(db_ficha)

        return db_ficha

    @staticmethod
    def buscar(session: Session, ficha_id: int) -> Optional[Ficha]:
        """Busca una ficha por su ID."""
        return session.get(Ficha, ficha_id)

    @staticmethod
    def buscar_por_numero(
        session: Session,
        numero_ficha: str
    ) -> Optional[Ficha]:
        """Busca una ficha por su número."""
        statement = select(Ficha).where(
            Ficha.numero_ficha == numero_ficha
        )

        return session.exec(statement).first()

    @staticmethod
    def actualizar(
        session: Session,
        ficha_id: int,
        ficha_update: FichaUpdate
    ) -> Optional[Ficha]:
        """Actualiza una ficha existente."""

        db_ficha = session.get(Ficha, ficha_id)

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
        """Elimina una ficha por su ID."""

        db_ficha = session.get(Ficha, ficha_id)

        if not db_ficha:
            return False

        session.delete(db_ficha)
        session.commit()

        return True

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Ficha]:
        """Lista las fichas."""

        statement = (
            select(Ficha)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()