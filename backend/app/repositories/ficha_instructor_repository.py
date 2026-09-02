from typing import List, Optional
from sqlmodel import Session, select
from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import FichaInstructorCreate, FichaInstructorUpdate

class FichaInstructorRepository:
    @staticmethod
    def crear(session: Session, ficha_instructor: FichaInstructorCreate) -> FichaInstructor:
        db = FichaInstructor(**ficha_instructor.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def buscar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return session.get(FichaInstructor, relacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[FichaInstructor]:
        return session.exec(select(FichaInstructor).offset(offset).limit(limit)).all()

    @staticmethod
    def listar_por_ficha(session: Session, id_ficha: int) -> List[FichaInstructor]:
        return session.exec(select(FichaInstructor).where(FichaInstructor.id_ficha == id_ficha)).all()

    @staticmethod
    def listar_por_ficha_y_periodo(session: Session, id_ficha: int, id_periodo: int) -> List[FichaInstructor]:
        return session.exec(select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha,
            FichaInstructor.id_periodo == id_periodo
        )).all()

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[FichaInstructor]:
        return session.exec(select(FichaInstructor).where(FichaInstructor.id_instructor == id_instructor)).all()

    @staticmethod
    def buscar_asignacion(session: Session, id_ficha: int, id_instructor: int, id_periodo: int) -> Optional[FichaInstructor]:
        return session.exec(select(FichaInstructor).where(
            FichaInstructor.id_ficha == id_ficha,
            FichaInstructor.id_instructor == id_instructor,
            FichaInstructor.id_periodo == id_periodo
        )).first()

    @staticmethod
    def actualizar(session: Session, relacion_id: int, update: FichaInstructorUpdate) -> Optional[FichaInstructor]:
        db = session.get(FichaInstructor, relacion_id)
        if not db: return None
        for k, v in update.model_dump(exclude_unset=True).items():
            setattr(db, k, v)
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def eliminar(session: Session, relacion_id: int) -> bool:
        db = session.get(FichaInstructor, relacion_id)
        if not db: return False
        session.delete(db)
        session.commit()
        return True
