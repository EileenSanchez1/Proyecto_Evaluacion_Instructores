from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.config.database import get_session
from app.services.respuesta_service import RespuestaService


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)


@router.get("/")
def generar_reporte(
    evaluacion_id: int = Query(...),
    session: Session = Depends(get_session)
):
    resultado = RespuestaService.calcular_puntaje(
        session,
        evaluacion_id
    )

    return {
        "evaluacion_id": evaluacion_id,
        "reporte": resultado
    }


@router.get("/instructor")
def generar_reporte_instructor(
    evaluacion_id: int = Query(...),
    instructor_id: int = Query(...),
    session: Session = Depends(get_session)
):
    resultado = RespuestaService.calcular_puntaje_por_instructor(
        session,
        evaluacion_id,
        instructor_id
    )

    return {
        "evaluacion_id": evaluacion_id,
        "reporte": resultado
    }