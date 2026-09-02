from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from app.config.database import get_session
from app.schemas.respuesta import RespuestaCreate, RespuestaRead, RespuestaUpdate
from app.services.respuesta_service import RespuestaService

router = APIRouter(prefix="/respuestas", tags=["Respuestas"])

@router.post("/", response_model=RespuestaRead)
def crear_respuesta(respuesta: RespuestaCreate, session: Session = Depends(get_session)):
    try:
        return RespuestaService.crear(session, respuesta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk", response_model=List[RespuestaRead])
def crear_respuestas_bulk(respuestas: List[RespuestaCreate], session: Session = Depends(get_session)):
    creadas = []
    for r in respuestas:
        try:
            creadas.append(RespuestaService.crear(session, r))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error en pregunta {r.id_pregunta}: {str(e)}")
    return creadas

@router.get("/", response_model=List[RespuestaRead])
def listar_respuestas(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)):
    return RespuestaService.listar(session, offset, limit)

@router.get("/{respuesta_id}", response_model=RespuestaRead)
def buscar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    r = RespuestaService.buscar(session, respuesta_id)
    if not r:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return r

@router.get("/evaluacion/{id_evaluacion}", response_model=List[RespuestaRead])
def listar_por_evaluacion(id_evaluacion: int, session: Session = Depends(get_session)):
    return RespuestaService.listar_por_evaluacion(session, id_evaluacion)

@router.put("/{respuesta_id}", response_model=RespuestaRead)
def actualizar_respuesta(respuesta_id: int, respuesta: RespuestaUpdate, session: Session = Depends(get_session)):
    try:
        r = RespuestaService.actualizar(session, respuesta_id, respuesta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not r:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return r

@router.delete("/{respuesta_id}")
def eliminar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    if not RespuestaService.eliminar(session, respuesta_id):
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return {"mensaje": "Respuesta eliminada correctamente"}
