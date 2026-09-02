from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.ficha import FichaCreate, FichaRead, FichaUpdate
from app.services.ficha_service import FichaService

router = APIRouter(prefix="/fichas", tags=["Fichas"])

# GET público: cualquiera puede ver las fichas (necesario para el registro de aprendices)
@router.get("/", response_model=List[FichaRead])
def listar_fichas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return FichaService.listar(session, offset, limit)

@router.get("/{ficha_id}", response_model=FichaRead)
def buscar_ficha(ficha_id: int, session: Session = Depends(get_session)):
    ficha = FichaService.buscar(session, ficha_id)
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return ficha

# POST/PUT/DELETE protegidos: solo admin/coordinador
@router.post("/", response_model=FichaRead, status_code=201, dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def crear_ficha(ficha: FichaCreate, session: Session = Depends(get_session)):
    try:
        return FichaService.crear(session, ficha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{ficha_id}", response_model=FichaRead, dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def actualizar_ficha(ficha_id: int, ficha: FichaUpdate, session: Session = Depends(get_session)):
    try:
        actualizada = FichaService.actualizar(session, ficha_id, ficha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not actualizada:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return actualizada

@router.delete("/{ficha_id}", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def eliminar_ficha(ficha_id: int, session: Session = Depends(get_session)):
    eliminada = FichaService.eliminar(session, ficha_id)
    if not eliminada:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return {"mensaje": "Ficha eliminada correctamente"}
