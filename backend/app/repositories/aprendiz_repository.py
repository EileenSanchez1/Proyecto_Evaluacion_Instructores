<<<<<<< HEAD
from typing import List, Optional

from sqlmodel import Session, select

=======
from sqlmodel import Session, select
from typing import List, Optional
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
from app.models.aprendiz import Aprendiz
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate


class AprendizRepository:

    @staticmethod
<<<<<<< HEAD
    def crear(
        session: Session,
        aprendiz: AprendizCreate
    ) -> Aprendiz:

        db_aprendiz = Aprendiz(
            **aprendiz.model_dump()
        )

        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)

        return db_aprendiz

    @staticmethod
    def buscar(
        session: Session,
        aprendiz_id: int
    ) -> Optional[Aprendiz]:

        return session.get(
            Aprendiz,
            aprendiz_id
        )

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ) -> Optional[Aprendiz]:

        statement = select(Aprendiz).where(
            Aprendiz.correo == correo
        )

        return session.exec(statement).first()

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Aprendiz]:

        statement = (
            select(Aprendiz)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[Aprendiz]:

        statement = select(Aprendiz).where(
            Aprendiz.id_ficha == id_ficha
        )

        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        aprendiz_id: int,
        aprendiz_update: AprendizUpdate
    ) -> Optional[Aprendiz]:

        db_aprendiz = session.get(
            Aprendiz,
            aprendiz_id
        )

        if not db_aprendiz:
            return None

        update_data = aprendiz_update.model_dump(
            exclude_unset=True
        )

=======
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        """Crea un nuevo aprendiz en la base de datos."""
        db_aprendiz = Aprendiz(**aprendiz.model_dump())
        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)
        return db_aprendiz

    @staticmethod
    def buscar(session: Session, aprendiz_id: int) -> Optional[Aprendiz]:
        """Busca un aprendiz por su ID."""
        return session.get(Aprendiz, aprendiz_id)

    @staticmethod
    def buscar_por_documento(session: Session, numero_documento: str) -> Optional[Aprendiz]:
        """Busca un aprendiz por su número de documento."""
        statement = select(Aprendiz).where(Aprendiz.numero_documento == numero_documento)
        return session.exec(statement).first()

    @staticmethod
    def buscar_por_correo(session: Session, correo: str) -> Optional[Aprendiz]:
        """Busca un aprendiz por su correo electrónico."""
        statement = select(Aprendiz).where(Aprendiz.correo_electronico == correo)
        return session.exec(statement).first()

    @staticmethod
    def actualizar(session: Session, aprendiz_id: int, aprendiz_update: AprendizUpdate) -> Optional[Aprendiz]:
        """Actualiza un aprendiz existente."""
        db_aprendiz = session.get(Aprendiz, aprendiz_id)
        if not db_aprendiz:
            return None

        update_data = aprendiz_update.model_dump(exclude_unset=True)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        for key, value in update_data.items():
            setattr(db_aprendiz, key, value)

        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)
<<<<<<< HEAD

        return db_aprendiz

    @staticmethod
    def eliminar(
        session: Session,
        aprendiz_id: int
    ) -> bool:

        db_aprendiz = session.get(
            Aprendiz,
            aprendiz_id
        )

=======
        return db_aprendiz

    @staticmethod
    def eliminar(session: Session, aprendiz_id: int) -> bool:
        """Elimina un aprendiz por su ID."""
        db_aprendiz = session.get(Aprendiz, aprendiz_id)
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        if not db_aprendiz:
            return False

        session.delete(db_aprendiz)
        session.commit()
<<<<<<< HEAD

        return True
=======
        return True

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Aprendiz]:
        """Lista todos los aprendices con paginación."""
        statement = select(Aprendiz).offset(offset).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def listar_por_ficha(session: Session, ficha_id: int) -> List[Aprendiz]:
        """Lista los aprendices de una ficha específica."""
        statement = select(Aprendiz).where(Aprendiz.ficha_id == ficha_id)
        return session.exec(statement).all()
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
