from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionRead, EvaluacionUpdate
from app.services.evaluacion_service import EvaluacionService

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])

@router.post("/", response_model=EvaluacionRead)
def crear_evaluacion(evaluacion: EvaluacionCreate, session: Session = Depends(get_session)):
    try:
        return EvaluacionService.crear(session, evaluacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[EvaluacionRead])
def listar_evaluaciones(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)):
    return EvaluacionService.listar(session, offset, limit)

@router.get("/{evaluacion_id}", response_model=EvaluacionRead)
def buscar_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    ev = EvaluacionService.buscar(session, evaluacion_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev

@router.get("/aprendiz/{id_aprendiz}", response_model=List[EvaluacionRead])
def listar_por_aprendiz(id_aprendiz: int, session: Session = Depends(get_session)):
    return EvaluacionService.listar_por_aprendiz(session, id_aprendiz)

@router.get("/instructor/{id_instructor}", response_model=List[EvaluacionRead])
def listar_por_instructor(id_instructor: int, session: Session = Depends(get_session)):
    return EvaluacionService.listar_por_instructor(session, id_instructor)

# Endpoint para que el aprendiz inicie una evaluación a un instructor
@router.post("/iniciar", response_model=EvaluacionRead)
def iniciar_evaluacion(
    id_aprendiz: int,
    id_instructor: int,
    id_periodo: int,
    session: Session = Depends(get_session)
):
    try:
        existente = EvaluacionService.buscar_por_aprendiz_instructor_periodo(
            session, id_aprendiz, id_instructor, id_periodo
        )
        if existente:
            return existente
        return EvaluacionService.crear(session, EvaluacionCreate(
            id_aprendiz=id_aprendiz,
            id_instructor=id_instructor,
            id_periodo=id_periodo,
            estado="Pendiente"
        ))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{evaluacion_id}", response_model=EvaluacionRead)
def actualizar_evaluacion(evaluacion_id: int, evaluacion: EvaluacionUpdate, session: Session = Depends(get_session)):
    ev = EvaluacionService.actualizar(session, evaluacion_id, evaluacion)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev

@router.put("/{evaluacion_id}/estado", response_model=EvaluacionRead)
def actualizar_estado(evaluacion_id: int, estado: str, session: Session = Depends(get_session)):
    ev = EvaluacionService.actualizar_estado(session, evaluacion_id, estado)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev

@router.delete("/{evaluacion_id}")
def eliminar_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    if not EvaluacionService.eliminar(session, evaluacion_id):
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return {"mensaje": "Evaluación eliminada correctamente"}
