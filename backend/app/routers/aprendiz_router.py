from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.aprendiz import (
    AprendizCreate,
    AprendizRead,
    AprendizUpdate
)
from app.services.aprendiz_service import AprendizService

router = APIRouter(
    prefix="/aprendices",
    tags=["Aprendices"]
)


@router.post("/", response_model=AprendizRead)
def crear_aprendiz(
    aprendiz: AprendizCreate,
    session: Session = Depends(get_session)
):
    try:
        return AprendizService.crear(session, aprendiz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[AprendizRead])
def listar_aprendices(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return AprendizService.listar(
        session,
        offset,
        limit
    )


@router.get("/{aprendiz_id}", response_model=AprendizRead)
def buscar_aprendiz(
    aprendiz_id: int,
    session: Session = Depends(get_session)
):
    aprendiz = AprendizService.buscar(
        session,
        aprendiz_id
    )

    if not aprendiz:
        raise HTTPException(
            status_code=404,
            detail="Aprendiz no encontrado"
        )

    return aprendiz


@router.put("/{aprendiz_id}", response_model=AprendizRead)
def actualizar_aprendiz(
    aprendiz_id: int,
    aprendiz_update: AprendizUpdate,
    session: Session = Depends(get_session)
):
    try:
        aprendiz = AprendizService.actualizar(
            session,
            aprendiz_id,
            aprendiz_update
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not aprendiz:
        raise HTTPException(
            status_code=404,
            detail="Aprendiz no encontrado"
        )

    return aprendiz


@router.delete("/{aprendiz_id}")
def eliminar_aprendiz(
    aprendiz_id: int,
    session: Session = Depends(get_session)
):
    eliminado = AprendizService.eliminar(
        session,
        aprendiz_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Aprendiz no encontrado"
        )

    return {
        "mensaje": "Aprendiz eliminado correctamente"
    }