<<<<<<< HEAD
from typing import List, Optional

from sqlmodel import Session, select

=======
from sqlmodel import Session, select
from typing import List, Optional
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from app.models.ficha import Ficha
from app.schemas.ficha import FichaCreate, FichaUpdate


class FichaRepository:

    @staticmethod
<<<<<<< HEAD
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

=======
    def crear(session: Session, ficha: FichaCreate) -> Ficha:
        """Crea una nueva ficha en la base de datos."""
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
    def buscar_por_numero(session: Session, numero_ficha: str) -> Optional[Ficha]:
        """Busca una ficha por su número."""
        statement = select(Ficha).where(Ficha.numero_ficha == numero_ficha)
        return session.exec(statement).first()

    @staticmethod
    def actualizar(session: Session, ficha_id: int, ficha_update: FichaUpdate) -> Optional[Ficha]:
        """Actualiza una ficha existente."""
        db_ficha = session.get(Ficha, ficha_id)
        if not db_ficha:
            return None

        update_data = ficha_update.model_dump(exclude_unset=True)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        for key, value in update_data.items():
            setattr(db_ficha, key, value)

        session.add(db_ficha)
        session.commit()
        session.refresh(db_ficha)
<<<<<<< HEAD

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

=======
        return db_ficha

    @staticmethod
    def eliminar(session: Session, ficha_id: int) -> bool:
        """Elimina una ficha por su ID."""
        db_ficha = session.get(Ficha, ficha_id)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        if not db_ficha:
            return False

        session.delete(db_ficha)
        session.commit()
<<<<<<< HEAD

        return True
=======
        return True

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Ficha]:
        """Lista todas las fichas con paginación."""
        statement = select(Ficha).offset(offset).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def listar_por_estado(session: Session, estado: str) -> List[Ficha]:
        """Lista las fichas filtradas por estado."""
        statement = select(Ficha).where(Ficha.estado == estado)
        return session.exec(statement).all()
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
