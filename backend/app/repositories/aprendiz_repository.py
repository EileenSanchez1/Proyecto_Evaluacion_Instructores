from typing import List, Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate


class AprendizRepository:

    @staticmethod
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

        for key, value in update_data.items():
            setattr(db_aprendiz, key, value)

        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)

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

        if not db_aprendiz:
            return False

        session.delete(db_aprendiz)
        session.commit()

        return True