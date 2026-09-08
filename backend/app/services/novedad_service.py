from sqlmodel import Session, select
from app.models.novedad import Novedad
from app.schemas.novedad import NovedadCreate
from typing import List

class NovedadService:
    @staticmethod
    def crear(session: Session, datos: NovedadCreate) -> Novedad:
        novedad = Novedad(**datos.model_dump())
        session.add(novedad)
        session.commit()
        session.refresh(novedad)
        return novedad

    @staticmethod
    def listar(session: Session) -> List[Novedad]:
        return session.exec(select(Novedad).order_by(Novedad.fecha.desc())).all()