from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import get_current_user, require_roles
from app.models.usuario import Usuario
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionRead, EvaluacionUpdate
from app.services.evaluacion_service import EvaluacionService

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


@router.post(
    "/",
    response_model=EvaluacionRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def crear_evaluacion(
    evaluacion: EvaluacionCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    """Crea evaluación. Aprendiz solo puede crear la suya; admin/coord pueden asistir."""
    try:
        # Si es aprendiz, forzar que id_aprendiz coincida con su vínculo (si existe)
        if usuario.rol and usuario.rol.nombre == "Aprendiz":
            from app.models.aprendiz import Aprendiz
            from sqlmodel import select

            aprendiz = session.exec(
                select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)
            ).first()
            if aprendiz and evaluacion.id_aprendiz != aprendiz.id_aprendiz:
                raise HTTPException(
                    status_code=403,
                    detail="Solo puedes crear evaluaciones para tu propio perfil de aprendiz.",
                )
        return EvaluacionService.crear(session, evaluacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=List[EvaluacionRead],
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def listar_evaluaciones(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return EvaluacionService.listar(session, offset, limit)


@router.get(
    "/{evaluacion_id}",
    response_model=EvaluacionRead,
    dependencies=[Depends(require_roles("Aprendiz", "Instructor", "Administrador", "Coordinador"))],
)
def buscar_evaluacion(
    evaluacion_id: int,
    session: Session = Depends(get_session),
):
    ev = EvaluacionService.buscar(session, evaluacion_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev


@router.get(
    "/aprendiz/{id_aprendiz}",
    response_model=List[EvaluacionRead],
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def listar_por_aprendiz(
    id_aprendiz: int,
    session: Session = Depends(get_session),
):
    return EvaluacionService.listar_por_aprendiz(session, id_aprendiz)


@router.get(
    "/instructor/{id_instructor}",
    response_model=List[EvaluacionRead],
    dependencies=[Depends(require_roles("Instructor", "Administrador", "Coordinador"))],
)
def listar_por_instructor(
    id_instructor: int,
    session: Session = Depends(get_session),
):
    return EvaluacionService.listar_por_instructor(session, id_instructor)


@router.post(
    "/iniciar",
    response_model=EvaluacionRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def iniciar_evaluacion(
    id_aprendiz: int,
    id_instructor: int,
    id_periodo: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Inicia (o reutiliza) una evaluación pendiente.
    Valida pertenencia a ficha/periodo y evita doble evaluación completada.
    """
    try:
        if usuario.rol and usuario.rol.nombre == "Aprendiz":
            from app.models.aprendiz import Aprendiz
            from sqlmodel import select

            aprendiz = session.exec(
                select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)
            ).first()
            if aprendiz and id_aprendiz != aprendiz.id_aprendiz:
                raise HTTPException(
                    status_code=403,
                    detail="Solo puedes iniciar evaluaciones de tu propio perfil.",
                )

        existente = EvaluacionService.buscar_por_aprendiz_instructor_periodo(
            session, id_aprendiz, id_instructor, id_periodo
        )
        if existente:
            estado = (existente.estado or "").strip().lower()
            if estado in ("completada", "finalizada", "enviada", "respondida", "evaluado"):
                raise HTTPException(
                    status_code=400,
                    detail="Ya completaste la evaluación de este instructor en este periodo.",
                )
            return existente

        return EvaluacionService.crear(
            session,
            EvaluacionCreate(
                id_aprendiz=id_aprendiz,
                id_instructor=id_instructor,
                id_periodo=id_periodo,
                estado="Pendiente",
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{evaluacion_id}",
    response_model=EvaluacionRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def actualizar_evaluacion(
    evaluacion_id: int,
    evaluacion: EvaluacionUpdate,
    session: Session = Depends(get_session),
):
    try:
        ev = EvaluacionService.actualizar(session, evaluacion_id, evaluacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev


@router.put(
    "/{evaluacion_id}/estado",
    response_model=EvaluacionRead,
    dependencies=[Depends(require_roles("Aprendiz", "Administrador", "Coordinador"))],
)
def actualizar_estado(
    evaluacion_id: int,
    estado: str,
    session: Session = Depends(get_session),
):
    try:
        ev = EvaluacionService.actualizar_estado(session, evaluacion_id, estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev


@router.delete(
    "/{evaluacion_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def eliminar_evaluacion(
    evaluacion_id: int,
    session: Session = Depends(get_session),
):
    if not EvaluacionService.eliminar(session, evaluacion_id):
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return {"mensaje": "Evaluación eliminada correctamente"}
