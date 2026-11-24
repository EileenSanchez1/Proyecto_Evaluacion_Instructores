"""Endpoints de reportes. La lógica está en los servicios app/services/reporte_*.py;
aquí solo se reciben los parámetros y se arma la respuesta HTTP."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlmodel import Session

from app.config.auth_dependencies import require_roles
from app.config.database import get_session
from app.models.instructor import Instructor
from app.services import reporte_avisos_service as avisos
from app.services import reporte_consolidado_service as consolidado
from app.services import reporte_preguntas_service as preguntas
from app.services import reporte_service
from app.services.respuesta_service import RespuestaService

router = APIRouter(prefix="/reportes", tags=["Reportes"])

ADMIN = [Depends(require_roles("Administrador", "Coordinador"))]
ADMIN_INSTRUCTOR = [Depends(require_roles("Instructor", "Administrador", "Coordinador"))]
MIME_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
FALTA_OPENPYXL = "Falta openpyxl. En el backend ejecuta: pip install openpyxl"


def _archivo(content: bytes, filename: str, media_type: str = MIME_EXCEL) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _error_500(mensaje: str, e: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=f"{mensaje}: {type(e).__name__}: {e}")


@router.get(
    "/",
    dependencies=[Depends(require_roles("Administrador", "Coordinador", "Aprendiz", "Instructor"))],
)
def generar_reporte(evaluacion_id: int = Query(...), session: Session = Depends(get_session)):
    resultado = RespuestaService.calcular_puntaje(session, evaluacion_id)
    return {"evaluacion_id": evaluacion_id, "reporte": resultado}


@router.get(
    "/instructor",
    dependencies=[Depends(require_roles("Administrador", "Coordinador", "Instructor"))],
)
def generar_reporte_instructor(
    evaluacion_id: int = Query(...),
    instructor_id: int = Query(...),
    session: Session = Depends(get_session),
):
    resultado = RespuestaService.calcular_puntaje_por_instructor(
        session, evaluacion_id, instructor_id
    )
    return {"evaluacion_id": evaluacion_id, "reporte": resultado}


@router.get("/dashboard", dependencies=ADMIN)
def reporte_dashboard(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    instructor_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    return reporte_service.dashboard(session, periodo_id, ficha_id, instructor_id)


@router.get("/historial", dependencies=ADMIN)
def historial_evaluaciones(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    return reporte_service.historial(session, periodo_id, ficha_id)


@router.get("/evaluacion/{evaluacion_id}/detalle", dependencies=ADMIN)
def detalle_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    """Detalle admin: preguntas, notas y solo observación general (sin obs por pregunta)."""
    detalle = reporte_service.detalle_evaluacion(session, evaluacion_id)
    if detalle is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return detalle


@router.get("/mis-evaluaciones", dependencies=ADMIN_INSTRUCTOR)
def mis_evaluaciones_instructor(
    instructor_id: int = Query(...),
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Historial de evaluaciones RECIBIDAS por un instructor (anónimo)."""
    return reporte_service.mis_evaluaciones(session, instructor_id, periodo_id)


@router.get("/instructor/{instructor_id}/preguntas", dependencies=ADMIN_INSTRUCTOR)
def reporte_por_preguntas(
    instructor_id: int,
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Desempeño del instructor por pregunta (evaluaciones en estado "Evaluado")."""
    return preguntas.por_preguntas(session, instructor_id, periodo_id, ficha_id)


@router.get("/mi-promedio", dependencies=ADMIN_INSTRUCTOR)
def mi_promedio_instructor(
    instructor_id: int = Query(...),
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Desempeño del instructor + fichas. Filtra por periodo si se envía periodo_id."""
    try:
        data = preguntas.por_preguntas(session, instructor_id, periodo_id, None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular promedio: {e}") from e
    return reporte_service.completar_mi_promedio(session, data, instructor_id, periodo_id)


# ── Pendientes de evaluación y sin foto ──────────────────────────────────────

@router.get("/pendientes-evaluacion", dependencies=ADMIN)
def pendientes_evaluacion(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Aprendices que aún no han evaluado a todos sus instructores del periodo."""
    return avisos.pendientes_evaluacion(session, periodo_id, ficha_id)


@router.get("/instructores-sin-foto", dependencies=ADMIN)
def instructores_sin_foto(session: Session = Depends(get_session)):
    """Lista instructores activos que aún no han subido foto."""
    return avisos.instructores_sin_foto(session)


@router.post("/enviar-recordatorio-pendientes", dependencies=ADMIN)
def enviar_recordatorio_pendientes(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Envía correo a aprendices con evaluaciones pendientes (plazo 24h)."""
    return avisos.enviar_recordatorio_pendientes(session, periodo_id, ficha_id)


@router.post("/enviar-advertencia-sin-foto", dependencies=ADMIN)
def enviar_advertencia_sin_foto(session: Session = Depends(get_session)):
    """Envía correo de advertencia a instructores sin foto."""
    return avisos.enviar_advertencia_sin_foto(session)


# ── Exportación Excel / PDF ──────────────────────────────────────────────────

@router.get("/exportar-pendientes-excel", dependencies=ADMIN)
def exportar_pendientes_excel(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Descarga Excel de aprendices que faltan por evaluar (por ficha / periodo)."""
    try:
        from app.services.export_service import excel_pendientes_evaluacion
    except ImportError:
        raise HTTPException(status_code=500, detail=FALTA_OPENPYXL)
    try:
        data = avisos.pendientes_evaluacion(session, periodo_id, ficha_id)
        content = excel_pendientes_evaluacion(data)
    except Exception as e:
        raise _error_500("Error generando Excel de pendientes", e)
    return _archivo(content, "pendientes_evaluacion.xlsx")


@router.get("/exportar-sin-foto-excel", dependencies=ADMIN)
def exportar_sin_foto_excel(session: Session = Depends(get_session)):
    """Descarga Excel de instructores que no han subido foto de perfil."""
    try:
        from app.services.export_service import excel_instructores_sin_foto
    except ImportError:
        raise HTTPException(status_code=500, detail=FALTA_OPENPYXL)
    try:
        content = excel_instructores_sin_foto(avisos.instructores_sin_foto(session))
    except Exception as e:
        raise _error_500("Error generando Excel sin foto", e)
    return _archivo(content, "instructores_sin_foto.xlsx")


@router.get(
    "/instructor/{instructor_id}/pdf",
    dependencies=[Depends(require_roles("Administrador", "Coordinador", "Instructor"))],
)
def exportar_instructor_pdf(
    instructor_id: int,
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """PDF por instructor: foto, nombre, correo, desempeño % y detalle por pregunta."""
    try:
        from app.services.export_pdf_service import pdf_reporte_instructor
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo cargar el generador de PDF. Instala reportlab: pip install reportlab. "
                f"({e})"
            ),
        )

    inst = session.get(Instructor, instructor_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    try:
        reporte = preguntas.por_preguntas(session, instructor_id, periodo_id, None)
    except Exception as e:
        raise _error_500("No se pudo obtener el reporte del instructor", e)

    data = preguntas.datos_pdf_instructor(session, inst, reporte, periodo_id)
    try:
        content = pdf_reporte_instructor(data)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Falta la librería reportlab. En el backend ejecuta: pip install reportlab",
        )
    except Exception as e:
        raise _error_500("Error generando PDF", e)
    return _archivo(content, f"reporte_instructor_{instructor_id}.pdf", "application/pdf")


@router.get("/exportar-consolidado-excel", dependencies=ADMIN)
def exportar_consolidado_excel(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Excel consolidado: hoja GENERAL + una hoja por instructor (Siempre/Algunas/Nunca)."""
    from app.services.export_service import excel_consolidado_evaluacion

    data = consolidado.datos_consolidado(session, periodo_id, ficha_id)
    return _archivo(excel_consolidado_evaluacion(data), "consolidado_evaluacion.xlsx")
