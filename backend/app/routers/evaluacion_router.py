from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.evaluacion import (
    EvaluacionCreate,
    EvaluacionRead,
    EvaluacionUpdate
)
from app.services.evaluacion_service import EvaluacionService

router = APIRouter(
    prefix="/evaluaciones",
    tags=["Evaluaciones"]
)


@router.post("/", response_model=EvaluacionRead)
def crear_evaluacion(
    evaluacion: EvaluacionCreate,
    session: Session = Depends(get_session)
):
    try:
        return EvaluacionService.crear(
            session,
            evaluacion
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_model=List[EvaluacionRead])
def listar_evaluaciones(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return EvaluacionService.listar(
        session,
        offset,
        limit
    )


@router.get("/{evaluacion_id}", response_model=EvaluacionRead)
def buscar_evaluacion(
    evaluacion_id: int,
    session: Session = Depends(get_session)
):
    evaluacion = EvaluacionService.buscar(
        session,
        evaluacion_id
    )

    if not evaluacion:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada"
        )

    return evaluacion


@router.put("/{evaluacion_id}", response_model=EvaluacionRead)
def actualizar_evaluacion(
    evaluacion_id: int,
    evaluacion_update: EvaluacionUpdate,
    session: Session = Depends(get_session)
):
    evaluacion = EvaluacionService.actualizar(
        session,
        evaluacion_id,
        evaluacion_update
    )

    if not evaluacion:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada"
        )

    return evaluacion


@router.patch("/{evaluacion_id}/estado")
def cambiar_estado(
    evaluacion_id: int,
    estado: str,
    session: Session = Depends(get_session)
):
    try:
        evaluacion = EvaluacionService.cambiar_estado(
            session,
            evaluacion_id,
            estado
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not evaluacion:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada"
        )

    return evaluacion


@router.delete("/{evaluacion_id}")
def eliminar_evaluacion(
    evaluacion_id: int,
    session: Session = Depends(get_session)
):
    eliminado = EvaluacionService.eliminar(
        session,
        evaluacion_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada"
        )

    return {
        "mensaje": "Evaluación eliminada correctamente"
    }