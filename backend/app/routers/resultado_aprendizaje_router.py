from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.resultado_aprendizaje import (
    ResultadoAprendizajeCreate,
    ResultadoAprendizajeRead,
    ResultadoAprendizajeUpdate,
)
from app.services.resultado_aprendizaje_service import ResultadoAprendizajeService


router = APIRouter(
    prefix="/resultados-aprendizaje",
    tags=["Resultados de Aprendizaje"]
)


@router.post(
    "/",
    response_model=ResultadoAprendizajeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def crear_resultado(
    data: ResultadoAprendizajeCreate,
    session: Session = Depends(get_session)
):
    try:
        return ResultadoAprendizajeService.crear(session, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ResultadoAprendizajeRead])
def listar_resultados(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return ResultadoAprendizajeService.listar(session, offset, limit)


@router.get("/{id_resultado}", response_model=ResultadoAprendizajeRead)
def buscar_resultado(
    id_resultado: int,
    session: Session = Depends(get_session)
):
    ra = ResultadoAprendizajeService.buscar(session, id_resultado)
    if not ra:
        raise HTTPException(
            status_code=404,
            detail="Resultado de aprendizaje no encontrado"
        )
    return ra


@router.put(
    "/{id_resultado}",
    response_model=ResultadoAprendizajeRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def actualizar_resultado(
    id_resultado: int,
    data: ResultadoAprendizajeUpdate,
    session: Session = Depends(get_session)
):
    try:
        ra = ResultadoAprendizajeService.actualizar(
            session, id_resultado, data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ra:
        raise HTTPException(
            status_code=404,
            detail="Resultado de aprendizaje no encontrado"
        )
    return ra


@router.delete(
    "/{id_resultado}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def eliminar_resultado(
    id_resultado: int,
    session: Session = Depends(get_session)
):
    """Desactiva (no borra) el resultado de aprendizaje."""
    ok = ResultadoAprendizajeService.eliminar(session, id_resultado)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Resultado de aprendizaje no encontrado"
        )
    return {
        "mensaje": (
            "Resultado de aprendizaje desactivado correctamente. "
            "Puedes reactivarlo cuando lo necesites."
        )
    }


@router.post(
    "/{id_resultado}/reactivar",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def reactivar_resultado(
    id_resultado: int,
    session: Session = Depends(get_session)
):
    ok = ResultadoAprendizajeService.reactivar(session, id_resultado)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Resultado de aprendizaje no encontrado"
        )
    return {"mensaje": "Resultado de aprendizaje reactivado correctamente."}
