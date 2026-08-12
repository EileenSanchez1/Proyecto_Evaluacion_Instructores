from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.pregunta import (
    PreguntaCreate,
    PreguntaRead,
    PreguntaUpdate
)
from app.services.pregunta_service import PreguntaService

router = APIRouter(
    prefix="/preguntas",
    tags=["Preguntas"]
)


@router.post("/", response_model=PreguntaRead)
def crear_pregunta(
    pregunta: PreguntaCreate,
    session: Session = Depends(get_session)
):
    return PreguntaService.crear(
        session,
        pregunta
    )


@router.get("/", response_model=List[PreguntaRead])
def listar_preguntas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return PreguntaService.listar(
        session,
        offset,
        limit
    )


@router.get("/activas", response_model=List[PreguntaRead])
def listar_preguntas_activas(
    session: Session = Depends(get_session)
):
    return PreguntaService.listar_activas(session)


@router.get("/{pregunta_id}", response_model=PreguntaRead)
def buscar_pregunta(
    pregunta_id: int,
    session: Session = Depends(get_session)
):
    pregunta = PreguntaService.buscar(
        session,
        pregunta_id
    )

    if not pregunta:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return pregunta


@router.put("/{pregunta_id}", response_model=PreguntaRead)
def actualizar_pregunta(
    pregunta_id: int,
    pregunta_update: PreguntaUpdate,
    session: Session = Depends(get_session)
):
    pregunta = PreguntaService.actualizar(
        session,
        pregunta_id,
        pregunta_update
    )

    if not pregunta:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return pregunta


@router.delete("/{pregunta_id}")
def eliminar_pregunta(
    pregunta_id: int,
    session: Session = Depends(get_session)
):
    eliminado = PreguntaService.eliminar(
        session,
        pregunta_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return {
        "mensaje": "Pregunta eliminada correctamente"
    }