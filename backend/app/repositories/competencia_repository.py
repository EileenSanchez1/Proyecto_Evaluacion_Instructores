from typing import List, Optional

from sqlmodel import Session, select

from app.models.competencia import Competencia
from app.schemas.competencia import CompetenciaCreate, CompetenciaUpdate


class CompetenciaRepository:

    @staticmethod
    def crear(
        session: Session,
        competencia: CompetenciaCreate
    ) -> Competencia:

        db_competencia = Competencia(
            **competencia.model_dump()
        )

        session.add(db_competencia)
        session.commit()
        session.refresh(db_competencia)

        return db_competencia

    @staticmethod
    def buscar(
        session: Session,
        competencia_id: int
    ) -> Optional[Competencia]:

        return session.get(
            Competencia,
            competencia_id
        )

    @staticmethod
    def buscar_por_nombre(
        session: Session,
        nombre: str
    ) -> Optional[Competencia]:

        statement = select(Competencia).where(
            Competencia.nombre == nombre
        )

        return session.exec(statement).first()

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Competencia]:

        statement = (
            select(Competencia)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def actualizar(
        session: Session,
        competencia_id: int,
        competencia_update: CompetenciaUpdate
    ) -> Optional[Competencia]:

        db_competencia = session.get(
            Competencia,
            competencia_id
        )

        if not db_competencia:
            return None

        update_data = competencia_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_competencia, key, value)

        session.add(db_competencia)
        session.commit()
        session.refresh(db_competencia)

        return db_competencia

    @staticmethod
    def eliminar(
        session: Session,
        competencia_id: int
    ) -> bool:

        db_competencia = session.get(
            Competencia,
            competencia_id
        )

        if not db_competencia:
            return False

        session.delete(db_competencia)
        session.commit()

        return True
