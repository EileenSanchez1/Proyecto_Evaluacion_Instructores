from typing import List, Optional
from sqlmodel import Session, select
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate

class EvaluacionRepository:
    @staticmethod
    def crear(session: Session, evaluacion: EvaluacionCreate) -> Evaluacion:
        db = Evaluacion(**evaluacion.model_dump())
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def buscar(session: Session, evaluacion_id: int) -> Optional[Evaluacion]:
        return session.get(Evaluacion, evaluacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Evaluacion]:
        return session.exec(select(Evaluacion).offset(offset).limit(limit)).all()

    @staticmethod
    def listar_por_aprendiz(session: Session, id_aprendiz: int) -> List[Evaluacion]:
        return session.exec(select(Evaluacion).where(Evaluacion.id_aprendiz == id_aprendiz)).all()

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[Evaluacion]:
        return session.exec(select(Evaluacion).where(Evaluacion.id_instructor == id_instructor)).all()

    @staticmethod
    def buscar_por_aprendiz_instructor_periodo(session: Session, id_aprendiz: int, id_instructor: int, id_periodo: int) -> Optional[Evaluacion]:
        return session.exec(select(Evaluacion).where(
            Evaluacion.id_aprendiz == id_aprendiz,
            Evaluacion.id_instructor == id_instructor,
            Evaluacion.id_periodo == id_periodo
        )).first()

    @staticmethod
    def listar_pendientes(session: Session) -> List[Evaluacion]:
        return session.exec(select(Evaluacion).where(Evaluacion.estado == "Pendiente")).all()

    @staticmethod
    def actualizar(session: Session, evaluacion_id: int, evaluacion_update: EvaluacionUpdate) -> Optional[Evaluacion]:
        db = session.get(Evaluacion, evaluacion_id)
        if not db: return None
        for k, v in evaluacion_update.model_dump(exclude_unset=True).items():
            setattr(db, k, v)
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def actualizar_estado(session: Session, evaluacion_id: int, estado: str) -> Optional[Evaluacion]:
        db = session.get(Evaluacion, evaluacion_id)
        if not db: return None
        db.estado = estado
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def eliminar(session: Session, evaluacion_id: int) -> bool:
        db = session.get(Evaluacion, evaluacion_id)
        if not db: return False
        session.delete(db)
        session.commit()
        return True
