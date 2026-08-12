from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.ficha_instructor import (
    FichaInstructorCreate,
    FichaInstructorRead,
    FichaInstructorUpdate
)
from app.services.ficha_instructor_service import FichaInstructorService


router = APIRouter(
    prefix="/ficha-instructores",
    tags=["Ficha-Instructores"]
)


@router.post("/", response_model=FichaInstructorRead)
def crear_ficha_instructor(
    ficha_instructor: FichaInstructorCreate,
    session: Session = Depends(get_session)
):
    try:
        return FichaInstructorService.crear(
            session,
            ficha_instructor
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_model=List[FichaInstructorRead])
def listar_ficha_instructores(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return FichaInstructorService.listar(
        session,
        offset,
        limit
    )


@router.get("/{relacion_id}", response_model=FichaInstructorRead)
def buscar_ficha_instructor(
    relacion_id: int,
    session: Session = Depends(get_session)
):
    relacion = FichaInstructorService.buscar(
        session,
        relacion_id
    )

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Asignación ficha-instructor no encontrada"
        )

    return relacion


@router.get("/ficha/{id_ficha}", response_model=List[FichaInstructorRead])
def listar_por_ficha(
    id_ficha: int,
    session: Session = Depends(get_session)
):
    return FichaInstructorService.listar_por_ficha(
        session,
        id_ficha
    )


@router.get(
    "/instructor/{id_instructor}",
    response_model=List[FichaInstructorRead]
)
def listar_por_instructor(
    id_instructor: int,
    session: Session = Depends(get_session)
):
    return FichaInstructorService.listar_por_instructor(
        session,
        id_instructor
    )


@router.put("/{relacion_id}", response_model=FichaInstructorRead)
def actualizar_ficha_instructor(
    relacion_id: int,
    ficha_instructor_update: FichaInstructorUpdate,
    session: Session = Depends(get_session)
):
    try:
        relacion = FichaInstructorService.actualizar(
            session,
            relacion_id,
            ficha_instructor_update
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Asignación ficha-instructor no encontrada"
        )

    return relacion


@router.delete("/{relacion_id}")
def eliminar_ficha_instructor(
    relacion_id: int,
    session: Session = Depends(get_session)
):
    eliminado = FichaInstructorService.eliminar(
        session,
        relacion_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Asignación ficha-instructor no encontrada"
        )

    return {
        "mensaje": "Asignación ficha-instructor eliminada correctamente"
    }