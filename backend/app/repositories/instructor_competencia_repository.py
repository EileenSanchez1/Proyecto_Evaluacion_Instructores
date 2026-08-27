from typing import List, Optional

from sqlmodel import Session, select

from app.models.instructor_competencia import InstructorCompetencia


class InstructorCompetenciaRepository:

    @staticmethod
    def crear(
        session: Session,
        id_instructor: int,
        id_competencia: int
    ) -> InstructorCompetencia:

        db_relacion = InstructorCompetencia(
            id_instructor=id_instructor,
            id_competencia=id_competencia
        )

        session.add(db_relacion)
        session.commit()
        session.refresh(db_relacion)

        return db_relacion

    @staticmethod
    def buscar_asignacion(
        session: Session,
        id_instructor: int,
        id_competencia: int
    ) -> Optional[InstructorCompetencia]:

        statement = select(InstructorCompetencia).where(
            InstructorCompetencia.id_instructor == id_instructor,
            InstructorCompetencia.id_competencia == id_competencia
        )

        return session.exec(statement).first()

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[InstructorCompetencia]:

        statement = select(InstructorCompetencia).where(
            InstructorCompetencia.id_instructor == id_instructor
        )

        return session.exec(statement).all()

    @staticmethod
    def eliminar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> None:

        relaciones = InstructorCompetenciaRepository.listar_por_instructor(
            session,
            id_instructor
        )

        for relacion in relaciones:
            session.delete(relacion)

        session.commit()

    @staticmethod
    def eliminar(
        session: Session,
        id_instructor: int,
        id_competencia: int
    ) -> bool:

        relacion = InstructorCompetenciaRepository.buscar_asignacion(
            session,
            id_instructor,
            id_competencia
        )

        if not relacion:
            return False

        session.delete(relacion)
        session.commit()

        return True
