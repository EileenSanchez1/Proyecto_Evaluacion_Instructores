from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.respuesta import (
    RespuestaCreate,
    RespuestaRead,
    RespuestaUpdate
)
from app.services.respuesta_service import RespuestaService

router = APIRouter(
    prefix="/respuestas",
    tags=["Respuestas"]
)


@router.post("/", response_model=RespuestaRead)
def crear_respuesta(
    respuesta: RespuestaCreate,
    session: Session = Depends(get_session)
):
    try:
        return RespuestaService.crear(
            session,
            respuesta
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_model=List[RespuestaRead])
def listar_respuestas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return RespuestaService.listar(
        session,
        offset,
        limit
    )


@router.get("/{respuesta_id}", response_model=RespuestaRead)
def buscar_respuesta(
    respuesta_id: int,
    session: Session = Depends(get_session)
):
    respuesta = RespuestaService.buscar(
        session,
        respuesta_id
    )

    if not respuesta:
        raise HTTPException(
            status_code=404,
            detail="Respuesta no encontrada"
        )

    return respuesta


@router.put("/{respuesta_id}", response_model=RespuestaRead)
def actualizar_respuesta(
    respuesta_id: int,
    respuesta_update: RespuestaUpdate,
    session: Session = Depends(get_session)
):
    try:
        respuesta = RespuestaService.actualizar(
            session,
            respuesta_id,
            respuesta_update
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not respuesta:
        raise HTTPException(
            status_code=404,
            detail="Respuesta no encontrada"
        )

    return respuesta


@router.delete("/{respuesta_id}")
def eliminar_respuesta(
    respuesta_id: int,
    session: Session = Depends(get_session)
):
    eliminado = RespuestaService.eliminar(
        session,
        respuesta_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Respuesta no encontrada"
        )

    return {
        "mensaje": "Respuesta eliminada correctamente"
    }