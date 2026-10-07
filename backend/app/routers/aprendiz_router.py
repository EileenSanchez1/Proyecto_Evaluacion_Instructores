from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlmodel import Session
from typing import List, Optional

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.aprendiz import (
    AprendizCreate,
    AprendizRead,
    AprendizUpdate
)
from app.services.aprendiz_service import AprendizService
from app.services.carga_aprendices_service import parsear_csv, cargar_desde_filas

router = APIRouter(
    prefix="/aprendices",
    tags=["Aprendices"]
)


@router.post(
    "/",
    response_model=AprendizRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def crear_aprendiz(
    aprendiz: AprendizCreate,
    session: Session = Depends(get_session)
):
    """Creación individual. Preferible usar carga masiva CSV desde coordinación."""
    try:
        return AprendizService.crear(session, aprendiz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/carga-masiva",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
async def carga_masiva_aprendices(
    archivo: UploadFile = File(...),
    id_periodo: Optional[int] = Form(None),
    enviar_correo: bool = Form(True),
    session: Session = Depends(get_session),
):
    """
    Sube un CSV/archivo plano con aprendices ya asignados a fichas.

    Columnas: nombre, apellido, correo, numero_ficha [, id_periodo]

    Por cada fila válida: crea usuario+aprendiz, genera contraseña temporal
    y envía correo (estilo SGVA / cartero) si enviar_correo=true.
    """
    nombre = (archivo.filename or "").lower()
    if not (
        nombre.endswith(".csv")
        or nombre.endswith(".txt")
        or nombre.endswith(".tsv")
        or "csv" in (archivo.content_type or "")
        or "text" in (archivo.content_type or "")
    ):
        raise HTTPException(
            status_code=400,
            detail="Sube un archivo CSV o TXT (separado por coma o punto y coma).",
        )

    contenido = await archivo.read()
    if not contenido.strip():
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    try:
        filas = parsear_csv(contenido)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el CSV: {e}")

    if not filas:
        raise HTTPException(status_code=400, detail="No hay filas de datos en el archivo.")

    resultado = cargar_desde_filas(
        session,
        filas,
        id_periodo_default=id_periodo,
        enviar_correo=enviar_correo,
    )
    return resultado


@router.get("/")
def listar_aprendices(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    session: Session = Depends(get_session)
):
    items = AprendizService.listar(session, offset, limit)
    return [AprendizService.to_read(session, a) for a in items]


@router.get("/por-ficha/{id_ficha}")
def listar_por_ficha(id_ficha: int, session: Session = Depends(get_session)):
    items = AprendizService.listar_por_ficha(session, id_ficha)
    return [AprendizService.to_read(session, a) for a in items]




@router.post(
    "/por-ficha/{id_ficha}/reenviar-correos",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def reenviar_correos_ficha(
    id_ficha: int,
    session: Session = Depends(get_session),
):
    """
    Genera contraseña temporal nueva y envía correo a todos los aprendices
    activos de la ficha (útil después de editar correos).
    """
    try:
        return AprendizService.reenviar_credenciales_ficha(session, id_ficha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{aprendiz_id}")
def buscar_aprendiz(
    aprendiz_id: int,
    session: Session = Depends(get_session)
):
    aprendiz = AprendizService.buscar(session, aprendiz_id)
    if not aprendiz:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return AprendizService.to_read(session, aprendiz)


@router.put(
    "/{aprendiz_id}",
    response_model=AprendizRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def actualizar_aprendiz(
    aprendiz_id: int,
    aprendiz_update: AprendizUpdate,
    session: Session = Depends(get_session)
):
    try:
        aprendiz = AprendizService.actualizar(
            session,
            aprendiz_id,
            aprendiz_update
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not aprendiz:
        raise HTTPException(
            status_code=404,
            detail="Aprendiz no encontrado"
        )

    return AprendizService.to_read(session, aprendiz)


@router.post(
    "/{aprendiz_id}/desactivar",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def desactivar_aprendiz(aprendiz_id: int, session: Session = Depends(get_session)):
    """Desertor / baja: no puede iniciar sesión. Se puede reactivar después."""
    try:
        ok = AprendizService.desactivar(session, aprendiz_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return {"mensaje": "Aprendiz desactivado. No podrá iniciar sesión hasta reactivarlo."}


@router.post(
    "/{aprendiz_id}/reactivar",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def reactivar_aprendiz(aprendiz_id: int, session: Session = Depends(get_session)):
    try:
        ok = AprendizService.reactivar(session, aprendiz_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return {"mensaje": "Aprendiz reactivado correctamente."}


@router.delete(
    "/{aprendiz_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def eliminar_aprendiz(
    aprendiz_id: int,
    session: Session = Depends(get_session)
):
    eliminado = AprendizService.eliminar(
        session,
        aprendiz_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Aprendiz no encontrado"
        )

    return {
        "mensaje": "Aprendiz eliminado correctamente"
    }
