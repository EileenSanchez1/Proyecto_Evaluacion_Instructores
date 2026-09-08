from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.models.novedad import Novedad
from app.schemas.novedad import NovedadCreate, NovedadRead, NovedadUpdate

router = APIRouter(prefix="/novedades", tags=["Novedades"])

@router.post("/", response_model=dict)
def crear_novedad(datos: NovedadCreate, session: Session = Depends(get_session)):
    novedad = Novedad(**datos.model_dump())
    session.add(novedad)
    session.commit()
    session.refresh(novedad)
    return {"mensaje": "Novedad enviada correctamente", "id_novedad": novedad.id_novedad}

@router.get("/", response_model=List[NovedadRead], dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def listar_novedades(session: Session = Depends(get_session)):
    return session.exec(select(Novedad).order_by(Novedad.fecha.desc())).all()

@router.patch("/{novedad_id}/leer", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def marcar_leida(novedad_id: int, session: Session = Depends(get_session)):
    novedad = session.get(Novedad, novedad_id)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    novedad.leido = True
    session.add(novedad)
    session.commit()
    return {"mensaje": "Novedad marcada como leída"}