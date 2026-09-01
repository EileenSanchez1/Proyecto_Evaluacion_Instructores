from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.periodo import PeriodoCreate, PeriodoRead, PeriodoUpdate
from app.services.periodo_service import PeriodoService


router = APIRouter(
    prefix="/periodos",
    tags=["Periodos"]
)


@router.post(
    "/",
    response_model=PeriodoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def crear_periodo(
    periodo: PeriodoCreate,
    session: Session = Depends(get_session)
):
    try:
        return PeriodoService.crear(session, periodo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/", response_model=List[PeriodoRead])
def listar_periodos(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 100
):
    return PeriodoService.listar(session, offset, limit)


@router.get("/activos", response_model=List[PeriodoRead])
def listar_periodos_activos(
    session: Session = Depends(get_session)
):
    return PeriodoService.listar_activos(session)


@router.get("/{periodo_id}", response_model=PeriodoRead)
def buscar_periodo(
    periodo_id: int,
    session: Session = Depends(get_session)
):
    periodo = PeriodoService.buscar(session, periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    return periodo


@router.put(
    "/{periodo_id}",
    response_model=PeriodoRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def actualizar_periodo(
    periodo_id: int,
    periodo_update: PeriodoUpdate,
    session: Session = Depends(get_session)
):
    try:
        periodo = PeriodoService.actualizar(session, periodo_id, periodo_update)
        if not periodo:
            raise HTTPException(status_code=404, detail="Periodo no encontrado")
        return periodo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{periodo_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def eliminar_periodo(
    periodo_id: int,
    session: Session = Depends(get_session)
):
    eliminado = PeriodoService.eliminar(session, periodo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    return {"mensaje": "Periodo eliminado correctamente"}
