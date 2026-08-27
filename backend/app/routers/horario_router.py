from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.horario import (
    HorarioCreate,
    HorarioRead,
    HorarioUpdate
)
from app.services.horario_service import HorarioService


router = APIRouter(
    prefix="/horarios",
    tags=["Horarios"]
)


@router.post(
    "/",
    response_model=HorarioRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def crear_horario(
    horario: HorarioCreate,
    session: Session = Depends(get_session)
):
    try:
        return HorarioService.crear(session, horario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[HorarioRead])
def listar_horarios(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return HorarioService.listar(session, offset, limit)


@router.get("/{horario_id}", response_model=HorarioRead)
def buscar_horario(
    horario_id: int,
    session: Session = Depends(get_session)
):
    horario = HorarioService.buscar(session, horario_id)

    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    return horario


@router.get("/instructor/{id_instructor}", response_model=List[HorarioRead])
def listar_horarios_por_instructor(
    id_instructor: int,
    session: Session = Depends(get_session)
):
    return HorarioService.listar_por_instructor(session, id_instructor)


@router.get("/ficha/{id_ficha}", response_model=List[HorarioRead])
def listar_horarios_por_ficha(
    id_ficha: int,
    session: Session = Depends(get_session)
):
    return HorarioService.listar_por_ficha(session, id_ficha)


@router.put(
    "/{horario_id}",
    response_model=HorarioRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def actualizar_horario(
    horario_id: int,
    horario_update: HorarioUpdate,
    session: Session = Depends(get_session)
):
    try:
        horario = HorarioService.actualizar(
            session,
            horario_id,
            horario_update
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    return horario


@router.delete(
    "/{horario_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def eliminar_horario(
    horario_id: int,
    session: Session = Depends(get_session)
):
    eliminado = HorarioService.eliminar(session, horario_id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    return {"mensaje": "Horario eliminado correctamente"}
