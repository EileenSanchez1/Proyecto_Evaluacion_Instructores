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
from app.models.pregunta import Pregunta
from app.services.respuesta_service import RespuestaService

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/")
def generar_reporte(evaluacion_id: int = Query(...), session: Session = Depends(get_session)):
    resultado = RespuestaService.calcular_puntaje(session, evaluacion_id)
    return {"evaluacion_id": evaluacion_id, "reporte": resultado}

@router.get("/instructor")
def generar_reporte_instructor(evaluacion_id: int = Query(...), instructor_id: int = Query(...), session: Session = Depends(get_session)):
    resultado = RespuestaService.calcular_puntaje_por_instructor(session, evaluacion_id, instructor_id)
    return {"evaluacion_id": evaluacion_id, "reporte": resultado}

@router.get("/dashboard", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
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
        return {"promedio_general": 0, "total_evaluaciones": 0, "instructores_evaluados": 0, "detalle_instructores": []}

    ids_evaluaciones = [e.id_evaluacion for e in evaluaciones]
    stmt_respuestas = select(Respuesta).where(Respuesta.id_evaluacion.in_(ids_evaluaciones))
    if instructor_id:
        stmt_respuestas = stmt_respuestas.where(Respuesta.id_instructor == instructor_id)
    respuestas = session.exec(stmt_respuestas).all()

    if not respuestas:
        return {"promedio_general": 0, "total_evaluaciones": len(evaluaciones), "instructores_evaluados": 0, "detalle_instructores": []}

    total_preguntas = len(respuestas)
    suma_total = sum(r.respuesta for r in respuestas)
    promedio_general = (suma_total / total_preguntas) if total_preguntas > 0 else 0

    instructor_stats = defaultdict(lambda: {"suma": 0, "total": 0})
    for r in respuestas:
        inst_id = r.id_instructor
        instructor_stats[inst_id]["total"] += 1
        instructor_stats[inst_id]["suma"] += r.respuesta

    detalle = []
    for inst_id, stats in instructor_stats.items():
        instructor = session.get(Instructor, inst_id)
        nombre = f"{instructor.nombre} {instructor.apellido}" if instructor else f"Instructor #{inst_id}"
        promedio = (stats["suma"] / stats["total"]) if stats["total"] > 0 else 0
        detalle.append({
            "id_instructor": inst_id,
            "nombre": nombre,
            "promedio": round(promedio, 2),
            "respuestas": stats["total"]
        })
    detalle.sort(key=lambda x: x["promedio"], reverse=True)

    return {
        "promedio_general": round(promedio_general, 2),
        "total_evaluaciones": len(evaluaciones),
        "instructores_evaluados": len(detalle),
        "detalle_instructores": detalle
    }

@router.get("/historial", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def historial_evaluaciones(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Evaluacion, Aprendiz, Ficha, Periodo, Instructor).join(
        Aprendiz, Evaluacion.id_aprendiz == Aprendiz.id_aprendiz
    ).join(
        Ficha, Aprendiz.id_ficha == Ficha.id_ficha
    ).join(
        Periodo, Evaluacion.id_periodo == Periodo.id_periodo
    ).join(
        Instructor, Evaluacion.id_instructor == Instructor.id_instructor
    )

    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)
    if ficha_id:
        statement = statement.where(Aprendiz.id_ficha == ficha_id)

    statement = statement.order_by(Evaluacion.fecha.desc())
    resultados = session.exec(statement).all()

    historial = []
    for evaluacion, aprendiz, ficha, periodo, instructor in resultados:
        historial.append({
            "id_evaluacion": evaluacion.id_evaluacion,
            "fecha": evaluacion.fecha.isoformat(),
            "estado": evaluacion.estado,
            "periodo": periodo.nombre,
            "aprendiz": f"{aprendiz.nombre} {aprendiz.apellido}",
            "ficha": ficha.numero_ficha,
            "programa": ficha.programa,
            "instructor": f"{instructor.nombre} {instructor.apellido}"
        })
    return historial

@router.get("/instructor/{instructor_id}/preguntas", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
def reporte_por_preguntas_admin(
    instructor_id: int,
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Devuelve el desempeño de un instructor agrupado por pregunta.
    Incluye: pregunta, promedio (1-5), porcentaje, fichas que evaluaron, mensaje.
    """
    statement = select(Evaluacion).where(
        Evaluacion.estado == "Evaluado",
        Evaluacion.id_instructor == instructor_id
    )
    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)

    evaluaciones = session.exec(statement).all()
    if not evaluaciones:
        return {"instructor_id": instructor_id, "preguntas": []}

    ids_evals = [e.id_evaluacion for e in evaluaciones]

    # Si hay filtro de ficha, filtrar evaluaciones por aprendiz
    if ficha_id:
        evals_filtradas = []
        for ev in evaluaciones:
            aprendiz = session.get(Aprendiz, ev.id_aprendiz)
            if aprendiz and aprendiz.id_ficha == ficha_id:
                evals_filtradas.append(ev)
        ids_evals = [e.id_evaluacion for e in evals_filtradas]
        if not ids_evals:
            return {"instructor_id": instructor_id, "preguntas": []}

    # Traer respuestas con preguntas
    stmt = select(Respuesta, Pregunta).join(Pregunta, Respuesta.id_pregunta == Pregunta.id_pregunta).where(
        Respuesta.id_evaluacion.in_(ids_evals),
        Respuesta.id_instructor == instructor_id
    ).order_by(Pregunta.orden)
    resultados = session.exec(stmt).all()

    # Agrupar por pregunta
    preguntas_data = defaultdict(lambda: {"suma": 0, "total": 0, "fichas": set()})
    for respuesta, pregunta in resultados:
        key = pregunta.id_pregunta
        preguntas_data[key]["suma"] += respuesta.respuesta
        preguntas_data[key]["total"] += 1
        preguntas_data[key]["descripcion"] = pregunta.descripcion
        preguntas_data[key]["orden"] = pregunta.orden
        # Ficha del aprendiz que respondió
        eval_obj = session.get(Evaluacion, respuesta.id_evaluacion)
        if eval_obj:
            aprendiz = session.get(Aprendiz, eval_obj.id_aprendiz)
            if aprendiz:
                ficha = session.get(Ficha, aprendiz.id_ficha)
                if ficha:
                    preguntas_data[key]["fichas"].add(ficha.numero_ficha)

    preguntas_list = []
    for pid, data in sorted(preguntas_data.items(), key=lambda x: x[1]["orden"]):
        promedio = data["suma"] / data["total"] if data["total"] > 0 else 0
        porcentaje = (promedio / 5) * 100

        if promedio >= 4.0:
            estado = "excelente"
            mensaje = "¡Excelente desempeño! Sigue así."
            color = "verde"
        elif promedio >= 3.0:
            estado = "mejorar"
            mensaje = f"Debes mejorar en: {data['descripcion']}"
            color = "amarillo"
        else:
            estado = "critico"
            mensaje = f"Estás fallando en: {data['descripcion']}. ¡Atención urgente!"
            color = "rojo"

        preguntas_list.append({
            "id_pregunta": pid,
            "orden": data["orden"],
            "pregunta": data["descripcion"],
            "promedio": round(promedio, 2),
            "porcentaje": round(porcentaje, 2),
            "total_respuestas": data["total"],
            "fichas": sorted(list(data["fichas"])),
            "estado": estado,
            "mensaje": mensaje,
            "color": color
        })

    return {
        "instructor_id": instructor_id,
        "preguntas": preguntas_list
    }

@router.get("/mi-promedio")
def mi_promedio_instructor(
    instructor_id: int = Query(...),
    session: Session = Depends(get_session)
):
    """
    Para el instructor logueado. Muestra su promedio por pregunta.
    """
    statement = select(Evaluacion).where(
        Evaluacion.estado == "Evaluado",
        Evaluacion.id_instructor == instructor_id
    )
    evaluaciones = session.exec(statement).all()
    if not evaluaciones:
        return {"instructor_id": instructor_id, "preguntas": []}

    ids_evals = [e.id_evaluacion for e in evaluaciones]

    stmt = select(Respuesta, Pregunta).join(Pregunta, Respuesta.id_pregunta == Pregunta.id_pregunta).where(
        Respuesta.id_evaluacion.in_(ids_evals),
        Respuesta.id_instructor == instructor_id
    ).order_by(Pregunta.orden)
    resultados = session.exec(stmt).all()

    preguntas_data = defaultdict(lambda: {"suma": 0, "total": 0, "fichas": set()})
    for respuesta, pregunta in resultados:
        key = pregunta.id_pregunta
        preguntas_data[key]["suma"] += respuesta.respuesta
        preguntas_data[key]["total"] += 1
        preguntas_data[key]["descripcion"] = pregunta.descripcion
        preguntas_data[key]["orden"] = pregunta.orden
        eval_obj = session.get(Evaluacion, respuesta.id_evaluacion)
        if eval_obj:
            aprendiz = session.get(Aprendiz, eval_obj.id_aprendiz)
            if aprendiz:
                ficha = session.get(Ficha, aprendiz.id_ficha)
                if ficha:
                    preguntas_data[key]["fichas"].add(ficha.numero_ficha)

    preguntas_list = []
    for pid, data in sorted(preguntas_data.items(), key=lambda x: x[1]["orden"]):
        promedio = data["suma"] / data["total"] if data["total"] > 0 else 0
        porcentaje = (promedio / 5) * 100

        if promedio >= 4.0:
            estado = "excelente"
            mensaje = "¡Excelente desempeño! Sigue así."
            color = "verde"
        elif promedio >= 3.0:
            estado = "mejorar"
            mensaje = f"Debes mejorar en: {data['descripcion']}"
            color = "amarillo"
        else:
            estado = "critico"
            mensaje = f"Estás fallando en: {data['descripcion']}. ¡Atención urgente!"
            color = "rojo"

        preguntas_list.append({
            "id_pregunta": pid,
            "orden": data["orden"],
            "pregunta": data["descripcion"],
            "promedio": round(promedio, 2),
            "porcentaje": round(porcentaje, 2),
            "total_respuestas": data["total"],
            "fichas": sorted(list(data["fichas"])),
            "estado": estado,
            "mensaje": mensaje,
            "color": color
        })

    return {
        "instructor_id": instructor_id,
        "preguntas": preguntas_list
    }