from typing import List, Optional
from sqlmodel import Session, select
from app.models.aprendiz import Aprendiz
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate

class AprendizRepository:
    @staticmethod
    def crear(session: Session, aprendiz: AprendizCreate) -> Aprendiz:
        db_aprendiz = Aprendiz(**aprendiz.model_dump())
        session.add(db_aprendiz)
        session.commit()
        session.refresh(db_aprendiz)
        return db_aprendiz

    @staticmethod
    def buscar(session: Session, aprendiz_id: int) -> Optional[Aprendiz]:
        return session.get(Aprendiz, aprendiz_id)

    @staticmethod
    def buscar_por_correo(session: Session, correo: str) -> Optional[Aprendiz]:
        return session.exec(select(Aprendiz).where(Aprendiz.correo == correo)).first()

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Aprendiz]:
        return session.exec(select(Aprendiz).offset(offset).limit(limit)).all()

    @staticmethod
    def listar_por_ficha(session: Session, id_ficha: int) -> List[Aprendiz]:
        return session.exec(select(Aprendiz).where(Aprendiz.id_ficha == id_ficha)).all()

    @staticmethod
    def listar_por_ficha_y_periodo(session: Session, id_ficha: int, id_periodo: int) -> List[Aprendiz]:
        return session.exec(select(Aprendiz).where(
            Aprendiz.id_ficha == id_ficha,
            Aprendiz.id_periodo == id_periodo
        )).all()

    @staticmethod
    def actualizar(session: Session, aprendiz_id: int, aprendiz_update: AprendizUpdate) -> Optional[Aprendiz]:
        db = session.get(Aprendiz, aprendiz_id)
        if not db: return None
        for k, v in aprendiz_update.model_dump(exclude_unset=True).items():
            setattr(db, k, v)
        session.add(db)
        session.commit()
        session.refresh(db)
        return db

    @staticmethod
    def eliminar(session: Session, aprendiz_id: int) -> bool:
        db = session.get(Aprendiz, aprendiz_id)
        if not db: return False
        session.delete(db)
        session.commit()
        return True
