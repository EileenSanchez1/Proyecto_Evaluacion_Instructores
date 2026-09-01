from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import Optional
from collections import defaultdict

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.models.evaluacion import Evaluacion
from app.models.respuesta import Respuesta
from app.models.aprendiz import Aprendiz
from app.models.ficha import Ficha
from app.models.instructor import Instructor
from app.models.periodo import Periodo
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


@router.get(
    "/dashboard",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def reporte_dashboard(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    instructor_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Evaluacion).where(Evaluacion.estado == "Evaluado")

    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)

    if ficha_id:
        statement = statement.join(Aprendiz).where(Aprendiz.id_ficha == ficha_id)

    evaluaciones = session.exec(statement).all()

    if not evaluaciones:
        return {
            "promedio_general": 0,
            "total_evaluaciones": 0,
            "instructores_evaluados": 0,
            "detalle_instructores": []
        }

    ids_evaluaciones = [e.id_evaluacion for e in evaluaciones]

    stmt_respuestas = select(Respuesta).where(
        Respuesta.id_evaluacion.in_(ids_evaluaciones)
    )

    if instructor_id:
        stmt_respuestas = stmt_respuestas.where(
            Respuesta.id_instructor == instructor_id
        )

    respuestas = session.exec(stmt_respuestas).all()

    if not respuestas:
        return {
            "promedio_general": 0,
            "total_evaluaciones": len(evaluaciones),
            "instructores_evaluados": 0,
            "detalle_instructores": []
        }

    total_preguntas = len(respuestas)
    cumple_count = sum(1 for r in respuestas if r.respuesta)
    promedio_general = (cumple_count / total_preguntas * 100) if total_preguntas > 0 else 0

    instructor_stats = defaultdict(lambda: {"cumple": 0, "total": 0})

    for r in respuestas:
        inst_id = r.id_instructor
        instructor_stats[inst_id]["total"] += 1
        if r.respuesta:
            instructor_stats[inst_id]["cumple"] += 1

    detalle = []
    for inst_id, stats in instructor_stats.items():
        instructor = session.get(Instructor, inst_id)
        nombre = f"{instructor.nombre} {instructor.apellido}" if instructor else f"Instructor #{inst_id}"
        promedio = (stats["cumple"] / stats["total"] * 100) if stats["total"] > 0 else 0
        detalle.append({
            "id_instructor": inst_id,
            "nombre": nombre,
            "promedio": round(promedio, 1),
            "respuestas": stats["total"]
        })

    detalle.sort(key=lambda x: x["promedio"], reverse=True)

    return {
        "promedio_general": round(promedio_general, 1),
        "total_evaluaciones": len(evaluaciones),
        "instructores_evaluados": len(detalle),
        "detalle_instructores": detalle
    }


@router.get(
    "/historial",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def historial_evaluaciones(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(
        Evaluacion,
        Aprendiz,
        Ficha,
        Periodo
    ).join(
        Aprendiz, Evaluacion.id_aprendiz == Aprendiz.id_aprendiz
    ).join(
        Ficha, Aprendiz.id_ficha == Ficha.id_ficha
    ).join(
        Periodo, Evaluacion.id_periodo == Periodo.id_periodo
    )

    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)
    if ficha_id:
        statement = statement.where(Aprendiz.id_ficha == ficha_id)

    statement = statement.order_by(Evaluacion.fecha.desc())

    resultados = session.exec(statement).all()

    historial = []
    for evaluacion, aprendiz, ficha, periodo in resultados:
        historial.append({
            "id_evaluacion": evaluacion.id_evaluacion,
            "fecha": evaluacion.fecha.isoformat(),
            "estado": evaluacion.estado,
            "periodo": periodo.nombre,
            "aprendiz": f"{aprendiz.nombre} {aprendiz.apellido}",
            "ficha": ficha.numero_ficha,
            "programa": ficha.programa
        })

    return historial
