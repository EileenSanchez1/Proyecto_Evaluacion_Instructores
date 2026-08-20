from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.ficha import FichaCreate, FichaRead, FichaUpdate
from app.services.ficha_service import FichaService

router = APIRouter(
    prefix="/fichas",
    tags=["Fichas"]
)


@router.post("/", response_model=FichaRead)
def crear_ficha(
    ficha: FichaCreate,
    session: Session = Depends(get_session)
):
    try:
        return FichaService.crear(session, ficha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[FichaRead])
def listar_fichas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return FichaService.listar(session, offset, limit)


@router.get("/{ficha_id}", response_model=FichaRead)
def buscar_ficha(
    ficha_id: int,
    session: Session = Depends(get_session)
):
    ficha = FichaService.buscar(session, ficha_id)

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha no encontrada"
        )

    return ficha


@router.put("/{ficha_id}", response_model=FichaRead)
def actualizar_ficha(
    ficha_id: int,
    ficha_update: FichaUpdate,
    session: Session = Depends(get_session)
):
    try:
        ficha = FichaService.actualizar(
            session,
            ficha_id,
            ficha_update
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha no encontrada"
        )

    return ficha


@router.delete("/{ficha_id}")
def eliminar_ficha(
    ficha_id: int,
    session: Session = Depends(get_session)
):
    eliminado = FichaService.eliminar(session, ficha_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Ficha no encontrada"
        )

    return {
        "mensaje": "Ficha eliminada correctamente"
    }