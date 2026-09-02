from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.ficha_instructor import FichaInstructorCreate, FichaInstructorRead, FichaInstructorUpdate
from app.services.ficha_instructor_service import FichaInstructorService

router = APIRouter(prefix="/ficha-instructores", tags=["Ficha-Instructores"])

@router.post("/", response_model=FichaInstructorRead, dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def crear(ficha_instructor: FichaInstructorCreate, session: Session = Depends(get_session)):
    try:
        return FichaInstructorService.crear(session, ficha_instructor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[FichaInstructorRead])
def listar(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)):
    return FichaInstructorService.listar(session, offset, limit)

@router.get("/{relacion_id}", response_model=FichaInstructorRead)
def buscar(relacion_id: int, session: Session = Depends(get_session)):
    r = FichaInstructorService.buscar(session, relacion_id)
    if not r: raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return r

@router.get("/ficha/{id_ficha}", response_model=List[FichaInstructorRead])
def por_ficha(id_ficha: int, session: Session = Depends(get_session)):
    return FichaInstructorService.listar_por_ficha(session, id_ficha)

@router.get("/ficha/{id_ficha}/periodo/{id_periodo}", response_model=List[FichaInstructorRead])
def por_ficha_y_periodo(id_ficha: int, id_periodo: int, session: Session = Depends(get_session)):
    return FichaInstructorService.listar_por_ficha_y_periodo(session, id_ficha, id_periodo)

@router.get("/instructor/{id_instructor}", response_model=List[FichaInstructorRead])
def por_instructor(id_instructor: int, session: Session = Depends(get_session)):
    return FichaInstructorService.listar_por_instructor(session, id_instructor)

@router.put("/{relacion_id}", response_model=FichaInstructorRead, dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def actualizar(relacion_id: int, update: FichaInstructorUpdate, session: Session = Depends(get_session)):
    try:
        r = FichaInstructorService.actualizar(session, relacion_id, update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not r: raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return r

@router.delete("/{relacion_id}", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def eliminar(relacion_id: int, session: Session = Depends(get_session)):
    if not FichaInstructorService.eliminar(session, relacion_id):
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return {"mensaje": "Asignación eliminada correctamente"}
