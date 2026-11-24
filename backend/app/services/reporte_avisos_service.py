"""Seguimiento: aprendices con evaluaciones pendientes, instructores sin foto
y los correos de recordatorio/advertencia para cada caso."""
from collections import defaultdict
from typing import Callable, Optional

from sqlmodel import Session, select

from app.models.aprendiz import Aprendiz
from app.models.evaluacion import Evaluacion
from app.models.ficha import Ficha
from app.models.ficha_instructor import FichaInstructor
from app.models.instructor import Instructor
from app.models.periodo import Periodo
from app.models.usuario import Usuario
from app.services.reporte_service import atributo, nombre_completo

ESTILO_CAJA = "font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;"
ESTILO_AVISO = "background:#fef3c7;padding:12px;border-radius:8px;color:#92400e;"
PIE = '<p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>'


# ── pendientes de evaluación ─────────────────────────────────────────────────

def _instructores_por_ficha(session: Session, periodo_id: int, ficha_id) -> dict:
    stmt = select(FichaInstructor).where(FichaInstructor.id_periodo == periodo_id)
    if ficha_id:
        stmt = stmt.where(FichaInstructor.id_ficha == ficha_id)
    fichas_inst = defaultdict(list)
    for a in session.exec(stmt).all():
        fichas_inst[a.id_ficha].append(a.id_instructor)
    return fichas_inst


def _aprendices(session: Session, ficha_id, ids_fichas: list):
    """Aprendices de la ficha indicada o de las fichas con asignación (None si no hay)."""
    stmt = select(Aprendiz)
    if ficha_id:
        stmt = stmt.where(Aprendiz.id_ficha == ficha_id)
    elif ids_fichas:
        stmt = stmt.where(Aprendiz.id_ficha.in_(ids_fichas))
    else:
        return None
    return session.exec(stmt).all()


def _evaluaciones_hechas(session: Session, periodo_id: int) -> set:
    evals = session.exec(
        select(Evaluacion).where(
            Evaluacion.id_periodo == periodo_id,
            Evaluacion.estado == "Evaluado",
        )
    ).all()
    return {(e.id_aprendiz, e.id_instructor) for e in evals}


def _instructor_pendiente(session: Session, id_inst: int) -> dict:
    inst = session.get(Instructor, id_inst)
    return {
        "id_instructor": id_inst,
        "nombre": nombre_completo(inst, f"#{id_inst}"),
        "correo": atributo(inst, "correo"),
    }


def _fila_pendiente(session: Session, ap, faltan: list) -> dict:
    ficha = session.get(Ficha, ap.id_ficha)
    return {
        "id_aprendiz": ap.id_aprendiz,
        "nombre": f"{ap.nombre} {ap.apellido}",
        "correo": ap.correo,
        "id_ficha": ap.id_ficha,
        "numero_ficha": atributo(ficha, "numero_ficha"),
        "instructores_pendientes": faltan,
        "total_pendientes": len(faltan),
    }


def pendientes_evaluacion(
    session: Session, periodo_id: Optional[int], ficha_id: Optional[int]
) -> dict:
    """Aprendices que aún no han evaluado a todos sus instructores del periodo."""
    if periodo_id is None:  # periodo activo si no se indica
        periodo = session.exec(select(Periodo).where(Periodo.estado == "Activo")).first()
        if not periodo:
            return {"periodo_id": None, "pendientes": [], "mensaje": "No hay periodo activo."}
        periodo_id = periodo.id_periodo

    fichas_inst = _instructores_por_ficha(session, periodo_id, ficha_id)
    aprendices = _aprendices(session, ficha_id, list(fichas_inst.keys()))
    if aprendices is None:
        return {"periodo_id": periodo_id, "pendientes": [], "total": 0}
    hechos = _evaluaciones_hechas(session, periodo_id)

    pendientes = []
    for ap in aprendices:
        faltan = [
            _instructor_pendiente(session, id_inst)
            for id_inst in fichas_inst.get(ap.id_ficha, [])
            if (ap.id_aprendiz, id_inst) not in hechos
        ]
        if faltan:
            pendientes.append(_fila_pendiente(session, ap, faltan))
    return {"periodo_id": periodo_id, "total": len(pendientes), "pendientes": pendientes}


# ── instructores sin foto ────────────────────────────────────────────────────

def _usuario_inactivo(session: Session, inst) -> bool:
    usuario = session.get(Usuario, inst.id_usuario) if inst.id_usuario else None
    return bool(usuario) and not usuario.activo


def instructores_sin_foto(session: Session) -> dict:
    """Instructores activos que aún no han subido foto."""
    sin_foto = [
        {
            "id_instructor": inst.id_instructor,
            "nombre": f"{inst.nombre} {inst.apellido}",
            "correo": inst.correo,
            "telefono": inst.telefono,
            "tiene_usuario": bool(inst.id_usuario),
        }
        for inst in session.exec(select(Instructor)).all()
        if not inst.foto and not _usuario_inactivo(session, inst)
    ]
    return {"total": len(sin_foto), "instructores": sin_foto}


# ── correos ──────────────────────────────────────────────────────────────────

def _enviar_lote(destinatarios: list, construir: Callable) -> tuple:
    """Envía un correo por destinatario. Devuelve (enviados, fallidos)."""
    from app.services.email_service import enviar_correo

    enviados = fallidos = 0
    for item in destinatarios:
        correo = item.get("correo")
        if correo and enviar_correo(correo, *construir(item)):
            enviados += 1
        else:
            fallidos += 1
    return enviados, fallidos


def _correo_recordatorio(p: dict) -> tuple:
    nombres_inst = ", ".join(i["nombre"] for i in p.get("instructores_pendientes", []))
    asunto = "Recordatorio: tienes evaluaciones pendientes — SENA"
    texto = (
        f"Hola {p['nombre']},\n\n"
        "Aún tienes instructores por evaluar en el periodo actual:\n"
        f"{nombres_inst}\n\n"
        "Tienes un plazo de 24 horas para completar las evaluaciones. "
        "Si no lo haces, se podrá generar un plan de mejora.\n\n"
        "— SENA · Evaluación de Instructores\n"
    )
    html = f"""
        <div style="{ESTILO_CAJA}">
          <h2 style="color:#39a900;">Evaluaciones pendientes</h2>
          <p>Hola <strong>{p['nombre']}</strong>,</p>
          <p>Aún debes evaluar a: <strong>{nombres_inst}</strong>.</p>
          <p style="{ESTILO_AVISO}">
            Plazo: <strong>24 horas</strong>. Si no completas las evaluaciones se podrá
            generar un plan de mejora.
          </p>
          {PIE}
        </div>
        """
    return asunto, texto, html


def _correo_sin_foto(inst: dict) -> tuple:
    asunto = "Advertencia: debes subir tu foto de perfil — SENA"
    texto = (
        f"Hola {inst['nombre']},\n\n"
        "Aún no has subido tu foto de perfil en el Sistema de Evaluación de Instructores.\n\n"
        "Debes subirla en un plazo razonable. Si no lo haces se podrá generar un plan de "
        "mejora o llamado de atención con el coordinador.\n\n"
        "Ingresa a la plataforma → Mi Perfil → actualiza tu foto.\n\n"
        "— SENA · Evaluación de Instructores\n"
    )
    html = f"""
        <div style="{ESTILO_CAJA}">
          <h2 style="color:#b45309;">Foto de perfil pendiente</h2>
          <p>Hola <strong>{inst['nombre']}</strong>,</p>
          <p>Aún no has subido tu <strong>foto de perfil</strong>.</p>
          <p style="{ESTILO_AVISO}">
            Si no la subes se podrá generar un plan de mejora o llamado de atención con el
            coordinador.
          </p>
          <p>Ingresa a <strong>Mi Perfil</strong> y actualiza tu foto.</p>
          {PIE}
        </div>
        """
    return asunto, texto, html


def enviar_recordatorio_pendientes(
    session: Session, periodo_id: Optional[int], ficha_id: Optional[int]
) -> dict:
    """Correo a aprendices con evaluaciones pendientes (plazo 24h)."""
    data = pendientes_evaluacion(session, periodo_id, ficha_id)
    enviados, fallidos = _enviar_lote(data.get("pendientes", []), _correo_recordatorio)
    return {"enviados": enviados, "fallidos": fallidos, "total_pendientes": data.get("total", 0)}


def enviar_advertencia_sin_foto(session: Session) -> dict:
    """Correo de advertencia a instructores sin foto."""
    data = instructores_sin_foto(session)
    enviados, fallidos = _enviar_lote(data.get("instructores", []), _correo_sin_foto)
    return {"enviados": enviados, "fallidos": fallidos, "total_sin_foto": data.get("total", 0)}
