from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.respuesta import RespuestaCreate, RespuestaRead, RespuestaUpdate
from app.services.respuesta_service import RespuestaService
from app.services.evaluacion_service import EvaluacionService

router = APIRouter(prefix="/respuestas", tags=["Respuestas"])


@router.post(
    "/",
    response_model=RespuestaRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def crear_respuesta(respuesta: RespuestaCreate, session: Session = Depends(get_session)):
    try:
        return RespuestaService.crear(session, respuesta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bulk",
    response_model=List[RespuestaRead],
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def crear_respuestas_bulk(
    respuestas: List[RespuestaCreate],
    marcar_evaluado: bool = True,
    session: Session = Depends(get_session),
):
    """
    Guarda todas las respuestas de una evaluación.
    Si marcar_evaluado=True (default), al terminar marca la evaluación como 'Evaluado'
    (estado que usa el frontend). Si una falla, se detiene sin marcar.
    """
    if not respuestas:
        raise HTTPException(status_code=400, detail="No se enviaron respuestas.")

    # Todas deben ser de la misma evaluación
    ids_eval = {r.id_evaluacion for r in respuestas}
    if len(ids_eval) != 1:
        raise HTTPException(
            status_code=400,
            detail="Todas las respuestas del lote deben pertenecer a la misma evaluación.",
        )
    id_evaluacion = next(iter(ids_eval))

    creadas = []
    for r in respuestas:
        try:
            creadas.append(RespuestaService.crear(session, r))
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error en pregunta {r.id_pregunta}: {str(e)}",
            )

    if marcar_evaluado and creadas:
        try:
            EvaluacionService.actualizar_estado(session, id_evaluacion, "Evaluado")
        except ValueError as e:
            # Las respuestas ya se guardaron; informar sin revertir
            raise HTTPException(
                status_code=400,
                detail=f"Respuestas guardadas, pero no se pudo cerrar la evaluación: {e}",
            )

    return creadas


@router.get(
    "/",
    response_model=List[RespuestaRead],
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def listar_respuestas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return RespuestaService.listar(session, offset, limit)


@router.get(
    "/{respuesta_id}",
    response_model=RespuestaRead,
    dependencies=[Depends(require_roles("Aprendiz", "Instructor", "Administrador", "Coordinador"))],
)
def buscar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    r = RespuestaService.buscar(session, respuesta_id)
    if not r:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return r


@router.get(
    "/evaluacion/{id_evaluacion}",
    response_model=List[RespuestaRead],
    dependencies=[Depends(require_roles("Aprendiz", "Instructor", "Administrador", "Coordinador"))],
)
def listar_por_evaluacion(
    id_evaluacion: int, session: Session = Depends(get_session)
):
    return RespuestaService.listar_por_evaluacion(session, id_evaluacion)


@router.put(
    "/{respuesta_id}",
    response_model=RespuestaRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def actualizar_respuesta(
    respuesta_id: int,
    respuesta: RespuestaUpdate,
    session: Session = Depends(get_session),
):
    try:
        r = RespuestaService.actualizar(session, respuesta_id, respuesta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not r:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return r


@router.delete(
    "/{respuesta_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def eliminar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    if not RespuestaService.eliminar(session, respuesta_id):
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return {"mensaje": "Respuesta eliminada correctamente"}
