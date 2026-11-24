"""Desempeño de un instructor por pregunta (y datos para su PDF).

Escala oficial de coordinación: Siempre=100%, Algunas veces=50%, Nunca=0%.
"""
import os
from collections import defaultdict
from typing import Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.evaluacion import Evaluacion
from app.models.ficha import Ficha
from app.models.periodo import Periodo
from app.models.pregunta import Pregunta
from app.models.respuesta import Respuesta

CATEGORIAS = ("siempre", "algunas", "nunca")
# Carpeta backend/ (este archivo está en backend/app/services/)
BASE_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _reporte_vacio(instructor_id: int) -> dict:
    return {
        "instructor_id": instructor_id,
        "promedio_general": 0,
        "porcentaje_general": 0,
        "total_respuestas": 0,
        "preguntas": [],
    }


def categoria(valor: int) -> Optional[str]:
    """5 o más = siempre, 3-4 = algunas, 1-2 = nunca, 0 = sin categoría."""
    if valor >= 5:
        return "siempre"
    if valor >= 3:
        return "algunas"
    if valor >= 1:
        return "nunca"
    return None


def _nueva_pregunta() -> dict:
    return {
        "suma": 0, "total": 0, "siempre": 0, "algunas": 0, "nunca": 0,
        "fichas": set(), "descripcion": "", "orden": 0,
    }


def _es_de_ficha(session: Session, evaluacion, ficha_id) -> bool:
    ap = session.get(Aprendiz, evaluacion.id_aprendiz)
    return bool(ap) and ap.id_ficha == int(ficha_id)


def _evaluaciones_evaluadas(session: Session, periodo_id, ficha_id) -> list:
    stmt = select(Evaluacion).where(Evaluacion.estado == "Evaluado")
    if periodo_id:
        stmt = stmt.where(Evaluacion.id_periodo == periodo_id)
    evaluaciones = session.exec(stmt).all()
    if ficha_id:
        evaluaciones = [e for e in evaluaciones if _es_de_ficha(session, e, ficha_id)]
    return evaluaciones


def _es_del_instructor(respuesta, mapa_eval: dict, instructor_id: int) -> bool:
    """Coincide por Respuesta.id_instructor o por Evaluacion.id_instructor."""
    if int(respuesta.id_instructor) == int(instructor_id):
        return True
    ev = mapa_eval.get(respuesta.id_evaluacion)
    return bool(ev) and int(ev.id_instructor) == int(instructor_id)


def _ficha_del_aprendiz(session: Session, id_aprendiz):
    ap = session.get(Aprendiz, id_aprendiz)
    return session.get(Ficha, ap.id_ficha) if ap else None


class _Acumulador:
    """Agrupa las respuestas por pregunta con conteos Siempre/Algunas/Nunca."""

    def __init__(self, session: Session, mapa_eval: dict):
        self.session = session
        self.mapa_eval = mapa_eval
        self.preguntas = defaultdict(_nueva_pregunta)
        self.totales = {c: 0 for c in CATEGORIAS}
        self.aprendices = set()
        self.observaciones = []

    def agregar(self, r) -> None:
        data = self.preguntas[r.id_pregunta]
        pregunta = self.session.get(Pregunta, r.id_pregunta)
        data["descripcion"] = getattr(pregunta, "descripcion", None) or f"Pregunta #{r.id_pregunta}"
        data["orden"] = (getattr(pregunta, "orden", 0) or 0) if pregunta else 0
        valor = int(r.respuesta or 0)
        data["suma"] += valor
        data["total"] += 1
        cat = categoria(valor)
        if cat:
            data[cat] += 1
            self.totales[cat] += 1
        ev = self.mapa_eval.get(r.id_evaluacion)
        if ev:
            self._agregar_evaluacion(data, ev)

    def _agregar_evaluacion(self, data: dict, ev) -> None:
        if getattr(ev, "id_aprendiz", None):
            self.aprendices.add(ev.id_aprendiz)
        obs = str(getattr(ev, "observacion_general", None) or "").strip()
        if obs:
            self.observaciones.append(obs)
        ficha = _ficha_del_aprendiz(self.session, ev.id_aprendiz)
        if ficha:
            data["fichas"].add(str(ficha.numero_ficha))


def _estado_pregunta(porcentaje: float, descripcion: str) -> tuple:
    if porcentaje >= 80:
        return "excelente", "¡Excelente desempeño! Cumples este criterio.", "verde"
    if porcentaje >= 50:
        return "mejorar", f"Debes mejorar en: {descripcion}", "amarillo"
    return "critico", f"Fallando en: {descripcion}. Requiere atención urgente.", "rojo"


def _resumen_pregunta(pid, data: dict) -> dict:
    tot = data["total"] or 1
    # % por pregunta = (S*100 + A*50 + N*0) / total
    porcentaje = round((data["siempre"] * 100 + data["algunas"] * 50) / tot, 1)
    promedio = round(data["suma"] / tot, 2)
    estado, mensaje, color = _estado_pregunta(porcentaje, data["descripcion"])
    return {
        "id_pregunta": pid,
        "orden": data["orden"],
        "pregunta": data["descripcion"],
        "texto_pregunta": data["descripcion"],
        "descripcion": data["descripcion"],
        "nota": promedio,
        "promedio": promedio,
        "porcentaje": porcentaje,
        "siempre": data["siempre"],
        "algunas": data["algunas"],
        "nunca": data["nunca"],
        "total_respuestas": data["total"],
        "fichas": sorted(data["fichas"]),
        "estado": estado,
        "mensaje": mensaje,
        "color": color,
    }


def _indicadores_generales(totales: dict) -> tuple:
    """(promedio 1-5, porcentaje 0-100, total) con la escala oficial."""
    s, a, n = (totales[c] for c in CATEGORIAS)
    total = s + a + n
    if not total:
        return 0, 0, 0
    porcentaje = round((s * 100 + a * 50) / total, 1)
    promedio = (s * 5 + a * 3 + n * 1) / total
    return promedio, porcentaje, total


def por_preguntas(
    session: Session,
    instructor_id: int,
    periodo_id: Optional[int] = None,
    ficha_id: Optional[int] = None,
) -> dict:
    """Desempeño del instructor por pregunta (solo evaluaciones en estado "Evaluado")."""
    evaluaciones = _evaluaciones_evaluadas(session, periodo_id, ficha_id)
    if not evaluaciones:
        return _reporte_vacio(instructor_id)

    mapa_eval = {e.id_evaluacion: e for e in evaluaciones}
    todas = session.exec(
        select(Respuesta).where(Respuesta.id_evaluacion.in_(list(mapa_eval)))
    ).all()
    respuestas = [r for r in todas if _es_del_instructor(r, mapa_eval, instructor_id)]
    if not respuestas:
        return _reporte_vacio(instructor_id)

    acumulado = _Acumulador(session, mapa_eval)
    for r in respuestas:
        acumulado.agregar(r)

    ordenadas = sorted(acumulado.preguntas.items(), key=lambda x: x[1]["orden"])
    preguntas = [_resumen_pregunta(pid, data) for pid, data in ordenadas]
    promedio, porcentaje, total = _indicadores_generales(acumulado.totales)
    return {
        "instructor_id": instructor_id,
        "promedio_general": round(promedio, 2),
        "porcentaje_general": porcentaje,
        "total_respuestas": total,
        "total_siempre": acumulado.totales["siempre"],
        "total_algunas": acumulado.totales["algunas"],
        "total_nunca": acumulado.totales["nunca"],
        "aprendices_evaluaron": len(acumulado.aprendices),
        "total_preguntas": len(preguntas),
        # observaciones únicas (máx 40)
        "observaciones": list(dict.fromkeys(acumulado.observaciones))[:40],
        "preguntas": preguntas,
    }


# ── datos para el PDF del instructor ─────────────────────────────────────────

def buscar_foto(foto) -> Optional[str]:
    """Ruta absoluta de la foto del instructor si existe en alguna carpeta conocida."""
    if not foto:
        return None
    nombre = os.path.basename(str(foto))
    candidatos = (
        os.path.join(BASE_BACKEND, str(foto).lstrip("/")),
        os.path.join(BASE_BACKEND, "app", "uploads", nombre),
        os.path.join(BASE_BACKEND, "uploads", nombre),
    )
    return next((c for c in candidatos if os.path.isfile(c)), None)


def datos_pdf_instructor(session: Session, inst, reporte: dict, periodo_id) -> dict:
    claves = (
        "promedio_general", "porcentaje_general", "total_siempre", "total_algunas",
        "total_nunca", "total_respuestas", "total_preguntas", "aprendices_evaluaron",
    )
    data = {
        "nombre": inst.nombre,
        "apellido": inst.apellido,
        "correo": inst.correo,
        "rol": getattr(inst, "planta_contrato", None) or "Instructor",
        "foto_path": buscar_foto(getattr(inst, "foto", None)),
        "preguntas": reporte.get("preguntas") or [],
        "observaciones": reporte.get("observaciones") or [],
        "periodo": None,
    }
    data.update({k: reporte.get(k) for k in claves})
    if periodo_id:
        data["periodo"] = getattr(session.get(Periodo, periodo_id), "nombre", None)
    return data
