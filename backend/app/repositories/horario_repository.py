from typing import List, Optional
from datetime import time

from sqlmodel import Session, select

from app.models.horario import Horario
from app.schemas.horario import HorarioCreate, HorarioUpdate


class HorarioRepository:

    @staticmethod
    def crear(
        session: Session,
        horario: HorarioCreate
    ) -> Horario:

        db_horario = Horario(
            **horario.model_dump()
        )

        session.add(db_horario)
        session.commit()
        session.refresh(db_horario)

        return db_horario

    @staticmethod
    def buscar(
        session: Session,
        horario_id: int
    ) -> Optional[Horario]:

        return session.get(
            Horario,
            horario_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Horario]:

        statement = (
            select(Horario)
            .offset(offset)
            .limit(limit)
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[Horario]:

        statement = select(Horario).where(
            Horario.id_instructor == id_instructor
        )

        return session.exec(statement).all()

    @staticmethod
    def listar_por_ficha(
        session: Session,
        id_ficha: int
    ) -> List[Horario]:

        statement = select(Horario).where(
            Horario.id_ficha == id_ficha
        )

        return session.exec(statement).all()

    @staticmethod
    def buscar_cruces(
        session: Session,
        id_instructor: int,
        dia: str,
        hora_inicio: time,
        hora_fin: time,
        excluir_id: Optional[int] = None
    ) -> List[Horario]:
        """
        Un cruce existe si, para el MISMO instructor y MISMO día,
        el rango [hora_inicio, hora_fin) se solapa con un horario
        ya registrado: inicio_nuevo < fin_existente Y fin_nuevo > inicio_existente.
        """

        statement = select(Horario).where(
            Horario.id_instructor == id_instructor,
            Horario.dia == dia,
            Horario.hora_inicio < hora_fin,
            Horario.hora_fin > hora_inicio
        )

        resultados = session.exec(statement).all()

        if excluir_id is not None:
            resultados = [
                h for h in resultados if h.id_horario != excluir_id
            ]

        return resultados

    @staticmethod
    def actualizar(
        session: Session,
        horario_id: int,
        horario_update: HorarioUpdate
    ) -> Optional[Horario]:

        db_horario = session.get(
            Horario,
            horario_id
        )

        if not db_horario:
            return None

        update_data = horario_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(db_horario, key, value)

        session.add(db_horario)
        session.commit()
        session.refresh(db_horario)

        return db_horario

    @staticmethod
    def eliminar(
        session: Session,
        horario_id: int
    ) -> bool:

        db_horario = session.get(
            Horario,
            horario_id
        )

        if not db_horario:
            return False

        session.delete(db_horario)
        session.commit()

        return True
