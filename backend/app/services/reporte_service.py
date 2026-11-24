"""Lógica de los reportes generales (dashboard, historial y detalle de evaluaciones).

Antes vivía dentro de app/routers/reporte_router.py; se separó para que el router
solo reciba la petición y devuelva la respuesta (mejor mantenibilidad).
"""
from collections import defaultdict
from typing import Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.evaluacion import Evaluacion
from app.models.ficha import Ficha
from app.models.ficha_instructor import FichaInstructor
from app.models.instructor import Instructor
from app.models.periodo import Periodo
from app.models.pregunta import Pregunta
from app.models.respuesta import Respuesta


# ── utilidades compartidas ───────────────────────────────────────────────────

def atributo(obj, nombre: str, defecto=None):
    """Devuelve obj.nombre o `defecto` si el objeto no existe."""
    return getattr(obj, nombre, defecto) if obj else defecto


def nombre_completo(persona, defecto=None):
    """'Nombre Apellido' de un aprendiz/instructor, o `defecto` si no existe."""
    return f"{persona.nombre} {persona.apellido}" if persona else defecto


def fecha_iso(fecha):
    """Fecha en formato ISO; si no se puede convertir, como texto."""
    if fecha is None:
        return None
    try:
        return fecha.isoformat()
    except Exception:
        return str(fecha)


# ── dashboard ────────────────────────────────────────────────────────────────

def _dashboard_vacio(total_evaluaciones: int) -> dict:
    return {
        "promedio_general": 0,
        "total_evaluaciones": total_evaluaciones,
        "instructores_evaluados": 0,
        "detalle_instructores": [],
    }


def _detalle_por_instructor(session: Session, respuestas) -> list:
    stats = defaultdict(lambda: {"suma": 0, "total": 0})
    for r in respuestas:
        stats[r.id_instructor]["total"] += 1
        stats[r.id_instructor]["suma"] += r.respuesta

    detalle = []
    for inst_id, s in stats.items():
        instructor = session.get(Instructor, inst_id)
        detalle.append({
            "id_instructor": inst_id,
            "nombre": nombre_completo(instructor, f"Instructor #{inst_id}"),
            "promedio": round(s["suma"] / s["total"], 2),
            "respuestas": s["total"],
        })
    detalle.sort(key=lambda x: x["promedio"], reverse=True)
    return detalle


def dashboard(
    session: Session,
    periodo_id: Optional[int],
    ficha_id: Optional[int],
    instructor_id: Optional[int],
) -> dict:
    statement = select(Evaluacion).where(Evaluacion.estado == "Evaluado")
    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)
    if ficha_id:
        statement = statement.join(Aprendiz).where(Aprendiz.id_ficha == ficha_id)
    evaluaciones = session.exec(statement).all()
    if not evaluaciones:
        return _dashboard_vacio(0)

    ids_evaluaciones = [e.id_evaluacion for e in evaluaciones]
    stmt_respuestas = select(Respuesta).where(Respuesta.id_evaluacion.in_(ids_evaluaciones))
    if instructor_id:
        stmt_respuestas = stmt_respuestas.where(Respuesta.id_instructor == instructor_id)
    respuestas = session.exec(stmt_respuestas).all()
    if not respuestas:
        return _dashboard_vacio(len(evaluaciones))

    promedio_general = sum(r.respuesta for r in respuestas) / len(respuestas)
    detalle = _detalle_por_instructor(session, respuestas)
    return {
        "promedio_general": round(promedio_general, 2),
        "total_evaluaciones": len(evaluaciones),
        "instructores_evaluados": len(detalle),
        "detalle_instructores": detalle,
    }


# ── historial ────────────────────────────────────────────────────────────────

def _nombre_o_guion(persona) -> str:
    return nombre_completo(persona, "—").strip()


def _fila_historial(evaluacion, aprendiz, ficha, periodo, instructor) -> dict:
    return {
        "id_evaluacion": evaluacion.id_evaluacion,
        "fecha": fecha_iso(evaluacion.fecha),
        "estado": evaluacion.estado or "Pendiente",
        "periodo": atributo(periodo, "nombre", "—"),
        "aprendiz": _nombre_o_guion(aprendiz),
        "ficha": atributo(ficha, "numero_ficha", "—"),
        "programa": atributo(ficha, "programa", "—"),
        "instructor": _nombre_o_guion(instructor),
    }


def historial(session: Session, periodo_id: Optional[int], ficha_id: Optional[int]) -> list:
    # LEFT OUTER JOIN: si falta aprendiz/ficha/periodo/instructor, la evaluación
    # sigue apareciendo (antes un INNER JOIN la ocultaba por completo).
    statement = (
        select(Evaluacion, Aprendiz, Ficha, Periodo, Instructor)
        .select_from(Evaluacion)
        .outerjoin(Aprendiz, Evaluacion.id_aprendiz == Aprendiz.id_aprendiz)
        .outerjoin(Ficha, Aprendiz.id_ficha == Ficha.id_ficha)
        .outerjoin(Periodo, Evaluacion.id_periodo == Periodo.id_periodo)
        .outerjoin(Instructor, Evaluacion.id_instructor == Instructor.id_instructor)
    )
    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)
    if ficha_id:
        # Solo aplica cuando hay aprendiz con esa ficha
        statement = statement.where(Aprendiz.id_ficha == ficha_id)
    statement = statement.order_by(Evaluacion.fecha.desc())

    return [
        _fila_historial(*fila)
        for fila in session.exec(statement).all()
        if fila[0] is not None
    ]


# ── detalle de una evaluación ────────────────────────────────────────────────

def etiqueta_escala(valor: int) -> str:
    """Escala oficial: 5=Siempre, 3=Algunas veces, 1=Nunca."""
    v = int(valor or 0)
    if v >= 5:
        return "Siempre"
    if v >= 3:
        return "Algunas veces"
    if v >= 1:
        return "Nunca"
    return "Sin respuesta"


def porcentaje_escala(valor: int) -> int:
    """Escala oficial: Siempre=100%, Algunas=50%, Nunca=0%."""
    if valor >= 5:
        return 100
    if valor >= 3:
        return 50
    return 0


def _item_respuesta(resp, preg) -> dict:
    valor = int(resp.respuesta or 0)
    return {
        "id_respuesta": resp.id_respuesta,
        "id_pregunta": preg.id_pregunta,
        "orden": getattr(preg, "orden", 0),
        "pregunta": preg.descripcion,
        "calificacion": valor,
        "etiqueta": etiqueta_escala(valor),
        "porcentaje": porcentaje_escala(valor),
        "observaciones": None,
    }


def _limpiar_observacion(obs):
    if obs:
        return str(obs).strip() or None
    return obs


def detalle_evaluacion(session: Session, evaluacion_id: int) -> Optional[dict]:
    """Detalle admin: preguntas, notas y solo observación general. None si no existe."""
    ev = session.get(Evaluacion, evaluacion_id)
    if not ev:
        return None

    aprendiz = session.get(Aprendiz, ev.id_aprendiz)
    ficha = session.get(Ficha, aprendiz.id_ficha) if aprendiz else None
    periodo = session.get(Periodo, ev.id_periodo)
    instructor = session.get(Instructor, ev.id_instructor)

    stmt = (
        select(Respuesta, Pregunta)
        .join(Pregunta, Respuesta.id_pregunta == Pregunta.id_pregunta)
        .where(Respuesta.id_evaluacion == evaluacion_id)
        .order_by(Pregunta.orden)
    )
    respuestas = [_item_respuesta(resp, preg) for resp, preg in session.exec(stmt).all()]

    return {
        "id_evaluacion": ev.id_evaluacion,
        "fecha": ev.fecha.isoformat() if ev.fecha else None,
        "estado": ev.estado,
        "periodo": atributo(periodo, "nombre"),
        "ficha": atributo(ficha, "numero_ficha"),
        "programa": atributo(ficha, "programa"),
        "aprendiz": nombre_completo(aprendiz),
        "instructor": nombre_completo(instructor),
        "respuestas": respuestas,
        "observaciones": [],  # compat: lista vacía; solo se usa observacion_general
        "observacion_general": _limpiar_observacion(getattr(ev, "observacion_general", None)),
    }


# ── vistas del instructor ────────────────────────────────────────────────────

def mis_evaluaciones(session: Session, instructor_id: int, periodo_id: Optional[int]) -> list:
    """Evaluaciones RECIBIDAS por un instructor, sin datos del aprendiz (anónimo)."""
    statement = (
        select(Evaluacion, Aprendiz, Ficha, Periodo)
        .join(Aprendiz, Evaluacion.id_aprendiz == Aprendiz.id_aprendiz)
        .join(Ficha, Aprendiz.id_ficha == Ficha.id_ficha)
        .join(Periodo, Evaluacion.id_periodo == Periodo.id_periodo)
        .where(Evaluacion.id_instructor == instructor_id)
        .order_by(Evaluacion.fecha.desc())
    )
    if periodo_id:
        statement = statement.where(Evaluacion.id_periodo == periodo_id)

    return [
        {
            "id_evaluacion": evaluacion.id_evaluacion,
            "fecha": evaluacion.fecha.isoformat() if evaluacion.fecha else None,
            "estado": evaluacion.estado,
            "periodo": atributo(periodo, "nombre"),
            "ficha": atributo(ficha, "numero_ficha"),
            "programa": atributo(ficha, "programa"),
        }
        for evaluacion, _aprendiz, ficha, periodo in session.exec(statement).all()
    ]


def fichas_asignadas(session: Session, instructor_id: int, periodo_id: Optional[int]) -> list:
    stmt = select(FichaInstructor).where(FichaInstructor.id_instructor == instructor_id)
    if periodo_id:
        stmt = stmt.where(FichaInstructor.id_periodo == periodo_id)

    resultado = []
    for a in session.exec(stmt).all():
        ficha = session.get(Ficha, a.id_ficha)
        periodo = session.get(Periodo, a.id_periodo)
        resultado.append({
            "id_ficha_instructor": a.id,
            "id_ficha": a.id_ficha,
            "numero_ficha": atributo(ficha, "numero_ficha"),
            "programa": atributo(ficha, "programa"),
            "id_periodo": a.id_periodo,
            "periodo": atributo(periodo, "nombre"),
        })
    return resultado


def completar_mi_promedio(
    session: Session, data, instructor_id: int, periodo_id: Optional[int]
) -> dict:
    """Agrega al reporte por preguntas las fichas asignadas y el nombre del instructor."""
    if not isinstance(data, dict):
        data = {}
    asignadas = fichas_asignadas(session, instructor_id, periodo_id)
    data["fichas_asignadas"] = asignadas
    data["total_fichas"] = len(asignadas)
    data["nombre_instructor"] = nombre_completo(session.get(Instructor, instructor_id))
    data["periodo_id"] = periodo_id
    return data
