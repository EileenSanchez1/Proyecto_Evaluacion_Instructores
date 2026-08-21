from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.schemas.instructor import (
    InstructorCreate,
    InstructorRead,
    InstructorUpdate
)
from app.services.instructor_service import InstructorService


router = APIRouter(
    prefix="/instructores",
    tags=["Instructores"]
)


@router.post("/", response_model=InstructorRead, status_code=status.HTTP_201_CREATED)
def crear_instructor(
    instructor: InstructorCreate,
    session: Session = Depends(get_session)
):
    try:
        return InstructorService.crear(
            session,
            instructor
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al crear instructor: {str(e)}"
        )


@router.get("/", response_model=List[InstructorRead])
def listar_instructores(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    try:
        return InstructorService.listar(
            session,
            offset,
            limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar instructores: {str(e)}"
        )


@router.get("/{instructor_id}", response_model=InstructorRead)
def buscar_instructor(
    instructor_id: int,
    session: Session = Depends(get_session)
):
    instructor = InstructorService.buscar(
        session,
        instructor_id
    )

    if not instructor:
        raise HTTPException(
            status_code=404,
            detail="Instructor no encontrado"
        )

    return instructor


@router.put("/{instructor_id}", response_model=InstructorRead)
def actualizar_instructor(
    instructor_id: int,
    instructor_update: InstructorUpdate,
    session: Session = Depends(get_session)
):
    try:
        instructor = InstructorService.actualizar(
            session,
            instructor_id,
            instructor_update
        )

        if not instructor:
            raise HTTPException(
                status_code=404,
                detail="Instructor no encontrado"
            )

        return instructor
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{instructor_id}")
def eliminar_instructor(
    instructor_id: int,
    session: Session = Depends(get_session)
):
    eliminado = InstructorService.eliminar(
        session,
        instructor_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Instructor no encontrado"
        )

    return {
        "mensaje": "Instructor eliminado correctamente"
    }