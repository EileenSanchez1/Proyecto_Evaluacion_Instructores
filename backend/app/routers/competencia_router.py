from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.competencia import (
    CompetenciaCreate,
    CompetenciaRead,
    CompetenciaUpdate
)
from app.services.competencia_service import CompetenciaService


router = APIRouter(
    prefix="/competencias",
    tags=["Competencias"]
)


@router.post(
    "/",
    response_model=CompetenciaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def crear_competencia(
    competencia: CompetenciaCreate,
    session: Session = Depends(get_session)
):
    try:
        return CompetenciaService.crear(session, competencia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CompetenciaRead])
def listar_competencias(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return CompetenciaService.listar(session, offset, limit)


@router.get("/{competencia_id}", response_model=CompetenciaRead)
def buscar_competencia(
    competencia_id: int,
    session: Session = Depends(get_session)
):
    competencia = CompetenciaService.buscar(session, competencia_id)

    if not competencia:
        raise HTTPException(
            status_code=404,
            detail="Competencia no encontrada"
        )

    return competencia


@router.put(
    "/{competencia_id}",
    response_model=CompetenciaRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def actualizar_competencia(
    competencia_id: int,
    competencia_update: CompetenciaUpdate,
    session: Session = Depends(get_session)
):
    try:
        competencia = CompetenciaService.actualizar(
            session,
            competencia_id,
            competencia_update
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not competencia:
        raise HTTPException(
            status_code=404,
            detail="Competencia no encontrada"
        )

    return competencia


@router.delete(
    "/{competencia_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def eliminar_competencia(
    competencia_id: int,
    session: Session = Depends(get_session)
):
    eliminado = CompetenciaService.eliminar(session, competencia_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Competencia no encontrada"
        )

    return {"mensaje": "Competencia eliminada correctamente"}
