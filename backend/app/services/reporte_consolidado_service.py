"""Datos del consolidado general de evaluación de instructores (estilo reporte SENA)."""
from collections import defaultdict
from typing import Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.evaluacion import Evaluacion
from app.models.instructor import Instructor
from app.models.periodo import Periodo
from app.models.pregunta import Pregunta
from app.models.respuesta import Respuesta
from app.services.reporte_service import nombre_completo

TITULO = "CONSOLIDADO GENERAL EVALUACIÓN INSTRUCTORES"
# bucket de la respuesta -> total al que suma
TOTAL_POR_BUCKET = {5: "total_s", 3: "total_a", 1: "total_n"}


def _periodo(session: Session, periodo_id: Optional[int]):
    """Periodo indicado o, si no se indica, el periodo activo."""
    if periodo_id:
        return session.get(Periodo, periodo_id)
    return session.exec(select(Periodo).where(Periodo.estado == "Activo")).first()


def _evaluaciones(session: Session, periodo, ficha_id: Optional[int]) -> list:
    statement = select(Evaluacion).where(Evaluacion.estado == "Evaluado")
    if periodo:
        statement = statement.where(Evaluacion.id_periodo == periodo.id_periodo)
    if ficha_id:
        statement = statement.join(Aprendiz).where(Aprendiz.id_ficha == ficha_id)
    return session.exec(statement).all()


def bucket(valor: int) -> int:
    """Agrupa la respuesta: 4-5 -> Siempre (5), 2-3 -> Algunas (3), resto -> Nunca (1)."""
    if valor >= 4:
        return 5
    if valor >= 2:
        return 3
    return 1


def _nuevo_instructor() -> dict:
    return {
        "por_pregunta": defaultdict(lambda: {5: 0, 3: 0, 1: 0}),
        "aprendices": set(),
        "obs": [],
        "total_s": 0,
        "total_a": 0,
        "total_n": 0,
        "total_r": 0,
    }


def _acumular(respuestas, eval_to_aprendiz: dict) -> dict:
    por_inst = defaultdict(_nuevo_instructor)
    for r in respuestas:
        d = por_inst[r.id_instructor]
        b = bucket(r.respuesta)
        d["por_pregunta"][r.id_pregunta][b] += 1
        d["total_r"] += 1
        d[TOTAL_POR_BUCKET[b]] += 1
        ap_id = eval_to_aprendiz.get(r.id_evaluacion)
        if ap_id:
            d["aprendices"].add(ap_id)
        obs = str(r.observaciones or "").strip()
        if obs:
            d["obs"].append(obs)
    return por_inst


def _orden(preg) -> int:
    return getattr(preg, "orden", 0) or 0


def _lista_preguntas(por_pregunta: dict, preguntas: dict) -> list:
    lista = []
    for pid, counts in sorted(por_pregunta.items(), key=lambda x: _orden(preguntas.get(x[0]))):
        preg = preguntas.get(pid)
        lista.append({
            "orden": getattr(preg, "orden", 0) if preg else 0,
            "enunciado": getattr(preg, "descripcion", f"Pregunta {pid}") if preg
            else f"Pregunta {pid}",
            "siempre": counts[5],
            "algunas": counts[3],
            "nunca": counts[1],
        })
    return lista


def _resumen_instructor(session: Session, inst_id: int, d: dict, preguntas: dict) -> dict:
    inst = session.get(Instructor, inst_id)
    total_r = d["total_r"] or 1
    # Escala oficial: Siempre=100, Algunas=50, Nunca=0
    porcentaje = round((100 * d["total_s"] + 50 * d["total_a"]) / total_r)
    return {
        "id_instructor": inst_id,
        "nombre": nombre_completo(inst, f"Instructor #{inst_id}"),
        "rol": getattr(inst, "planta_contrato", None) or "Técnico",
        "aprendices_evaluaron": len(d["aprendices"]),
        "porcentaje": porcentaje,
        "preguntas": _lista_preguntas(d["por_pregunta"], preguntas),
        "total_siempre": d["total_s"],
        "total_algunas": d["total_a"],
        "total_nunca": d["total_n"],
        "total_respuestas": d["total_r"],
        "observaciones": list(dict.fromkeys(d["obs"]))[:50],
    }


def _fecha_aplicacion(periodo) -> str:
    inicio = getattr(periodo, "fecha_inicio", None)
    fin = getattr(periodo, "fecha_fin", None)
    return f"{inicio} AL {fin}" if inicio and fin else ""


def datos_consolidado(
    session: Session, periodo_id: Optional[int], ficha_id: Optional[int]
) -> dict:
    """Hoja GENERAL + una hoja por instructor con conteos Siempre/Algunas/Nunca."""
    periodo = _periodo(session, periodo_id)
    evaluaciones = _evaluaciones(session, periodo, ficha_id)
    data = {
        "titulo": TITULO,
        "periodo_nombre": getattr(periodo, "nombre", "") if periodo else "",
        "fecha_aplicacion": "",
        "instructores": [],
    }
    if not evaluaciones:
        return data

    ids_eval = [e.id_evaluacion for e in evaluaciones]
    respuestas = session.exec(select(Respuesta).where(Respuesta.id_evaluacion.in_(ids_eval))).all()
    preguntas = {p.id_pregunta: p for p in session.exec(select(Pregunta)).all()}
    eval_to_aprendiz = {e.id_evaluacion: e.id_aprendiz for e in evaluaciones}

    por_inst = _acumular(respuestas, eval_to_aprendiz)
    instructores = [
        _resumen_instructor(session, inst_id, d, preguntas) for inst_id, d in por_inst.items()
    ]
    instructores.sort(key=lambda x: x["porcentaje"], reverse=True)
    data["fecha_aplicacion"] = _fecha_aplicacion(periodo)
    data["instructores"] = instructores
    return data
