from fastapi import APIRouter, HTTPException, Depends, Query
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



@router.get("/evaluacion/{evaluacion_id}/detalle")
def detalle_evaluacion(
    evaluacion_id: int,
    session: Session = Depends(get_session),
):
    """Detalle admin: preguntas, notas y solo observación general (sin obs por pregunta)."""
    from app.models.respuesta import Respuesta as RespModel
    from app.models.pregunta import Pregunta as PregModel

    ev = session.get(Evaluacion, evaluacion_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    aprendiz = session.get(Aprendiz, ev.id_aprendiz)
    ficha = session.get(Ficha, aprendiz.id_ficha) if aprendiz else None
    periodo = session.get(Periodo, ev.id_periodo)
    instructor = session.get(Instructor, ev.id_instructor)

    stmt = (
        select(RespModel, PregModel)
        .join(PregModel, RespModel.id_pregunta == PregModel.id_pregunta)
        .where(RespModel.id_evaluacion == evaluacion_id)
        .order_by(PregModel.orden)
    )
    rows = session.exec(stmt).all()

    def _etiqueta_escala(valor: int) -> str:
        # Escala oficial: 5=Siempre, 3=Algunas veces, 1=Nunca
        v = int(valor or 0)
        if v >= 5:
            return "Siempre"
        if v >= 3:
            return "Algunas veces"
        if v >= 1:
            return "Nunca"
        return "Sin respuesta"

    respuestas = []
    for resp, preg in rows:
        valor = int(resp.respuesta or 0)
        item = {
            "id_respuesta": resp.id_respuesta,
            "id_pregunta": preg.id_pregunta,
            "orden": getattr(preg, "orden", 0),
            "pregunta": preg.descripcion,
            "calificacion": valor,
            "etiqueta": _etiqueta_escala(valor),
            # Escala oficial: Siempre=100%, Algunas=50%, Nunca=0%
            "porcentaje": (100 if valor >= 5 else (50 if valor >= 3 else (0 if valor >= 1 else 0))),
            "observaciones": None,
        }
        respuestas.append(item)

    obs_general = getattr(ev, "observacion_general", None)
    if obs_general:
        obs_general = str(obs_general).strip() or None

    return {
        "id_evaluacion": ev.id_evaluacion,
        "fecha": ev.fecha.isoformat() if ev.fecha else None,
        "estado": ev.estado,
        "periodo": periodo.nombre if periodo else None,
        "ficha": ficha.numero_ficha if ficha else None,
        "programa": ficha.programa if ficha else None,
        "aprendiz": f"{aprendiz.nombre} {aprendiz.apellido}" if aprendiz else None,
        "instructor": f"{instructor.nombre} {instructor.apellido}" if instructor else None,
        "respuestas": respuestas,
        "observaciones": [],  # compat: lista vacía; solo se usa observacion_general
        "observacion_general": obs_general,
    }


@router.get("/mis-evaluaciones")
def mis_evaluaciones_instructor(
    instructor_id: int = Query(...),
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """
    Historial de evaluaciones RECIBIDAS por un instructor (anónimo).
    No incluye nombre del aprendiz: solo ficha, programa, fecha, estado y periodo.
    """
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
    resultados = session.exec(statement).all()

    items = []
    for evaluacion, aprendiz, ficha, periodo in resultados:
        items.append({
            "id_evaluacion": evaluacion.id_evaluacion,
            "fecha": evaluacion.fecha.isoformat() if evaluacion.fecha else None,
            "estado": evaluacion.estado,
            "periodo": periodo.nombre if periodo else None,
            "ficha": ficha.numero_ficha if ficha else None,
            "programa": ficha.programa if ficha else None,
            # Anónimo: sin datos del aprendiz
        })
    return items


@router.get("/instructor/{instructor_id}/preguntas")
def reporte_por_preguntas(
    instructor_id: int,
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Desempeño del instructor por pregunta.
    Misma base de datos que el dashboard: respuestas de evaluaciones en estado
    "Evaluado", filtradas por instructor (en respuesta o en la evaluación).
    No pierde filas si una pregunta fue desactivada/borrada (outer load).
    """
    from sqlalchemy import or_

    # 1) Evaluaciones evaluadas (igual que dashboard)
    stmt_eval = select(Evaluacion).where(Evaluacion.estado == "Evaluado")
    if periodo_id:
        stmt_eval = stmt_eval.where(Evaluacion.id_periodo == periodo_id)
    evaluaciones = session.exec(stmt_eval).all()

    if ficha_id:
        evaluaciones = [
            e
            for e in evaluaciones
            if (ap := session.get(Aprendiz, e.id_aprendiz))
            and ap.id_ficha == int(ficha_id)
        ]

    if not evaluaciones:
        return {
            "instructor_id": instructor_id,
            "promedio_general": 0,
            "porcentaje_general": 0,
            "total_respuestas": 0,
            "preguntas": [],
        }

    ids_eval = [e.id_evaluacion for e in evaluaciones]
    mapa_eval = {e.id_evaluacion: e for e in evaluaciones}

    # 2) Respuestas de esas evaluaciones para este instructor
    #    (coincide con dashboard: Respuesta.id_instructor, y además Evaluacion.id_instructor)
    stmt_resp = select(Respuesta).where(Respuesta.id_evaluacion.in_(ids_eval))
    todas = session.exec(stmt_resp).all()
    respuestas = [
        r
        for r in todas
        if int(r.id_instructor) == int(instructor_id)
        or (
            mapa_eval.get(r.id_evaluacion)
            and int(mapa_eval[r.id_evaluacion].id_instructor) == int(instructor_id)
        )
    ]

    if not respuestas:
        return {
            "instructor_id": instructor_id,
            "promedio_general": 0,
            "porcentaje_general": 0,
            "total_respuestas": 0,
            "preguntas": [],
        }

    # 3) Agrupar por pregunta con conteos Siempre/Algunas/Nunca
    # Escala oficial coordinación: Siempre=100%, Algunas=50%, Nunca=0%
    preguntas_data = defaultdict(
        lambda: {
            "suma": 0,
            "total": 0,
            "siempre": 0,
            "algunas": 0,
            "nunca": 0,
            "fichas": set(),
            "descripcion": "",
            "orden": 0,
        }
    )
    total_s = total_a = total_n = 0
    aprendices = set()
    observaciones = []
    for r in respuestas:
        key = r.id_pregunta
        pregunta = session.get(Pregunta, key)
        descripcion = (
            pregunta.descripcion
            if pregunta and getattr(pregunta, "descripcion", None)
            else f"Pregunta #{key}"
        )
        orden = getattr(pregunta, "orden", 0) or 0 if pregunta else 0
        val = int(r.respuesta or 0)
        preguntas_data[key]["suma"] += val
        preguntas_data[key]["total"] += 1
        preguntas_data[key]["descripcion"] = descripcion
        preguntas_data[key]["orden"] = orden
        if val >= 5:
            preguntas_data[key]["siempre"] += 1
            total_s += 1
        elif val >= 3:
            preguntas_data[key]["algunas"] += 1
            total_a += 1
        elif val >= 1:
            preguntas_data[key]["nunca"] += 1
            total_n += 1
        ev = mapa_eval.get(r.id_evaluacion)
        if ev:
            if getattr(ev, "id_aprendiz", None):
                aprendices.add(ev.id_aprendiz)
            obs = getattr(ev, "observacion_general", None)
            if obs and str(obs).strip():
                observaciones.append(str(obs).strip())
            ap = session.get(Aprendiz, ev.id_aprendiz)
            if ap:
                ficha = session.get(Ficha, ap.id_ficha)
                if ficha:
                    preguntas_data[key]["fichas"].add(str(ficha.numero_ficha))

    total_g = total_s + total_a + total_n
    preguntas_list = []
    for pid, data in sorted(preguntas_data.items(), key=lambda x: x[1]["orden"]):
        tot = data["total"] or 1
        # % por pregunta = (S*100 + A*50 + N*0) / total
        porcentaje = round(
            (data["siempre"] * 100 + data["algunas"] * 50) / tot, 1
        )
        promedio = data["suma"] / tot
        if porcentaje >= 80:
            estado, mensaje, color = (
                "excelente",
                "¡Excelente desempeño! Cumples este criterio.",
                "verde",
            )
        elif porcentaje >= 50:
            estado, mensaje, color = (
                "mejorar",
                f"Debes mejorar en: {data['descripcion']}",
                "amarillo",
            )
        else:
            estado, mensaje, color = (
                "critico",
                f"Fallando en: {data['descripcion']}. Requiere atención urgente.",
                "rojo",
            )
        preguntas_list.append(
            {
                "id_pregunta": pid,
                "orden": data["orden"],
                "pregunta": data["descripcion"],
                "texto_pregunta": data["descripcion"],
                "descripcion": data["descripcion"],
                "nota": round(promedio, 2),
                "promedio": round(promedio, 2),
                "porcentaje": porcentaje,
                "siempre": data["siempre"],
                "algunas": data["algunas"],
                "nunca": data["nunca"],
                "total_respuestas": data["total"],
                "fichas": sorted(list(data["fichas"])),
                "estado": estado,
                "mensaje": mensaje,
                "color": color,
            }
        )

    # Promedio instructor oficial: (S*100 + A*50 + N*0) / total_respuestas
    pct_g = round((total_s * 100 + total_a * 50) / total_g, 1) if total_g else 0
    prom_g = ((total_s * 5 + total_a * 3 + total_n * 1) / total_g) if total_g else 0
    # observaciones únicas (máx 40)
    obs_unicas = list(dict.fromkeys(observaciones))[:40]
    return {
        "instructor_id": instructor_id,
        "promedio_general": round(prom_g, 2),
        "porcentaje_general": pct_g,
        "total_respuestas": total_g,
        "total_siempre": total_s,
        "total_algunas": total_a,
        "total_nunca": total_n,
        "aprendices_evaluaron": len(aprendices),
        "total_preguntas": len(preguntas_list),
        "observaciones": obs_unicas,
        "preguntas": preguntas_list,
    }


@router.get("/mi-promedio")
def mi_promedio_instructor(
    instructor_id: int = Query(...),
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Desempeño del instructor + fichas. Filtra por periodo si se envía periodo_id."""
    try:
        data = reporte_por_preguntas(
            instructor_id=instructor_id,
            periodo_id=periodo_id,
            ficha_id=None,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular promedio: {e}") from e

    from app.models.ficha_instructor import FichaInstructor
    from app.models.periodo import Periodo as PeriodoModel

    stmt = select(FichaInstructor).where(FichaInstructor.id_instructor == instructor_id)
    if periodo_id:
        stmt = stmt.where(FichaInstructor.id_periodo == periodo_id)
    asignaciones = session.exec(stmt).all()

    fichas_asignadas = []
    for a in asignaciones:
        ficha = session.get(Ficha, a.id_ficha)
        periodo = session.get(PeriodoModel, a.id_periodo)
        fichas_asignadas.append({
            "id_ficha_instructor": a.id,
            "id_ficha": a.id_ficha,
            "numero_ficha": getattr(ficha, "numero_ficha", None) if ficha else None,
            "programa": (getattr(ficha, "programa", None) if ficha else None),
            "id_periodo": a.id_periodo,
            "periodo": getattr(periodo, "nombre", None) if periodo else None,
        })

    instructor = session.get(Instructor, instructor_id)
    if not isinstance(data, dict):
        data = {}
    data["fichas_asignadas"] = fichas_asignadas
    data["total_fichas"] = len(fichas_asignadas)
    data["nombre_instructor"] = (
        f"{instructor.nombre} {instructor.apellido}" if instructor else None
    )
    data["periodo_id"] = periodo_id
    return data


# ── Pendientes de evaluación y sin foto ──────────────────────────────────────

@router.get(
    "/pendientes-evaluacion",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def pendientes_evaluacion(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """
    Lista aprendices que aún no han evaluado a todos sus instructores
    del periodo (y opcionalmente de una ficha).
    """
    from app.models.ficha_instructor import FichaInstructor
    from app.models.periodo import Periodo as PeriodoModel

    # Periodo activo si no se indica
    if periodo_id is None:
        periodo = session.exec(
            select(PeriodoModel).where(PeriodoModel.estado == "Activo")
        ).first()
        if not periodo:
            return {"periodo_id": None, "pendientes": [], "mensaje": "No hay periodo activo."}
        periodo_id = periodo.id_periodo

    # Asignaciones instructor-ficha del periodo
    stmt_asig = select(FichaInstructor).where(FichaInstructor.id_periodo == periodo_id)
    if ficha_id:
        stmt_asig = stmt_asig.where(FichaInstructor.id_ficha == ficha_id)
    asignaciones = session.exec(stmt_asig).all()

    # Mapa ficha -> lista de instructores
    from collections import defaultdict
    fichas_inst = defaultdict(list)
    for a in asignaciones:
        fichas_inst[a.id_ficha].append(a.id_instructor)

    # Aprendices de esas fichas
    stmt_ap = select(Aprendiz)
    if ficha_id:
        stmt_ap = stmt_ap.where(Aprendiz.id_ficha == ficha_id)
    else:
        ids_fichas = list(fichas_inst.keys())
        if not ids_fichas:
            return {"periodo_id": periodo_id, "pendientes": [], "total": 0}
        stmt_ap = stmt_ap.where(Aprendiz.id_ficha.in_(ids_fichas))
    aprendices = session.exec(stmt_ap).all()

    # Evaluaciones ya hechas en el periodo
    evals = session.exec(
        select(Evaluacion).where(
            Evaluacion.id_periodo == periodo_id,
            Evaluacion.estado == "Evaluado",
        )
    ).all()
    hechos = {(e.id_aprendiz, e.id_instructor) for e in evals}

    pendientes = []
    for ap in aprendices:
        instructores_ficha = fichas_inst.get(ap.id_ficha, [])
        faltan = []
        for id_inst in instructores_ficha:
            if (ap.id_aprendiz, id_inst) not in hechos:
                inst = session.get(Instructor, id_inst)
                faltan.append({
                    "id_instructor": id_inst,
                    "nombre": f"{inst.nombre} {inst.apellido}" if inst else f"#{id_inst}",
                    "correo": inst.correo if inst else None,
                })
        if faltan:
            ficha = session.get(Ficha, ap.id_ficha)
            pendientes.append({
                "id_aprendiz": ap.id_aprendiz,
                "nombre": f"{ap.nombre} {ap.apellido}",
                "correo": ap.correo,
                "id_ficha": ap.id_ficha,
                "numero_ficha": getattr(ficha, "numero_ficha", None) if ficha else None,
                "instructores_pendientes": faltan,
                "total_pendientes": len(faltan),
            })

    return {
        "periodo_id": periodo_id,
        "total": len(pendientes),
        "pendientes": pendientes,
    }


@router.get(
    "/instructores-sin-foto",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def instructores_sin_foto(session: Session = Depends(get_session)):
    """Lista instructores activos que aún no han subido foto."""
    from app.models.usuario import Usuario

    todos = session.exec(select(Instructor)).all()
    sin_foto = []
    for inst in todos:
        if inst.foto:
            continue
        usuario = session.get(Usuario, inst.id_usuario) if inst.id_usuario else None
        if usuario and not usuario.activo:
            continue
        sin_foto.append({
            "id_instructor": inst.id_instructor,
            "nombre": f"{inst.nombre} {inst.apellido}",
            "correo": inst.correo,
            "telefono": inst.telefono,
            "tiene_usuario": bool(inst.id_usuario),
        })
    return {"total": len(sin_foto), "instructores": sin_foto}


@router.post(
    "/enviar-recordatorio-pendientes",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def enviar_recordatorio_pendientes(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Envía correo a aprendices con evaluaciones pendientes (plazo 24h)."""
    from app.services.email_service import enviar_correo

    data = pendientes_evaluacion(periodo_id=periodo_id, ficha_id=ficha_id, session=session)
    enviados = 0
    fallidos = 0
    for p in data.get("pendientes", []):
        correo = p.get("correo")
        if not correo:
            fallidos += 1
            continue
        nombres_inst = ", ".join(i["nombre"] for i in p.get("instructores_pendientes", []))
        asunto = "Recordatorio: tienes evaluaciones pendientes — SENA"
        texto = (
            f"Hola {p['nombre']},\n\n"
            f"Aún tienes instructores por evaluar en el periodo actual:\n"
            f"{nombres_inst}\n\n"
            f"Tienes un plazo de 24 horas para completar las evaluaciones. "
            f"Si no lo haces, se podrá generar un plan de mejora.\n\n"
            f"— SENA · Evaluación de Instructores\n"
        )
        html = f"""
        <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
          <h2 style="color:#39a900;">Evaluaciones pendientes</h2>
          <p>Hola <strong>{p['nombre']}</strong>,</p>
          <p>Aún debes evaluar a: <strong>{nombres_inst}</strong>.</p>
          <p style="background:#fef3c7;padding:12px;border-radius:8px;color:#92400e;">
            Plazo: <strong>24 horas</strong>. Si no completas las evaluaciones se podrá generar un plan de mejora.
          </p>
          <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
        </div>
        """
        ok = enviar_correo(correo, asunto, texto, html)
        if ok:
            enviados += 1
        else:
            fallidos += 1
    return {"enviados": enviados, "fallidos": fallidos, "total_pendientes": data.get("total", 0)}


@router.post(
    "/enviar-advertencia-sin-foto",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def enviar_advertencia_sin_foto(session: Session = Depends(get_session)):
    """Envía correo de advertencia a instructores sin foto."""
    from app.services.email_service import enviar_correo

    data = instructores_sin_foto(session=session)
    enviados = 0
    fallidos = 0
    for inst in data.get("instructores", []):
        correo = inst.get("correo")
        if not correo:
            fallidos += 1
            continue
        asunto = "Advertencia: debes subir tu foto de perfil — SENA"
        texto = (
            f"Hola {inst['nombre']},\n\n"
            f"Aún no has subido tu foto de perfil en el Sistema de Evaluación de Instructores.\n\n"
            f"Debes subirla en un plazo razonable. Si no lo haces se podrá generar un plan de mejora "
            f"o llamado de atención con el coordinador.\n\n"
            f"Ingresa a la plataforma → Mi Perfil → actualiza tu foto.\n\n"
            f"— SENA · Evaluación de Instructores\n"
        )
        html = f"""
        <div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
          <h2 style="color:#b45309;">Foto de perfil pendiente</h2>
          <p>Hola <strong>{inst['nombre']}</strong>,</p>
          <p>Aún no has subido tu <strong>foto de perfil</strong>.</p>
          <p style="background:#fef3c7;padding:12px;border-radius:8px;color:#92400e;">
            Si no la subes se podrá generar un plan de mejora o llamado de atención con el coordinador.
          </p>
          <p>Ingresa a <strong>Mi Perfil</strong> y actualiza tu foto.</p>
          <p style="color:#9ca3af;font-size:12px;">SENA · Evaluación de Instructores</p>
        </div>
        """
        ok = enviar_correo(correo, asunto, texto, html)
        if ok:
            enviados += 1
        else:
            fallidos += 1
    return {"enviados": enviados, "fallidos": fallidos, "total_sin_foto": data.get("total", 0)}


# ── Exportación Excel ─────────────────────────────────────────────────────────

@router.get(
    "/exportar-pendientes-excel",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def exportar_pendientes_excel(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """Descarga Excel de aprendices que faltan por evaluar (por ficha / periodo)."""
    from fastapi.responses import Response

    try:
        from app.services.export_service import excel_pendientes_evaluacion
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Falta openpyxl. En el backend ejecuta: pip install openpyxl",
        )

    try:
        data = pendientes_evaluacion(
            periodo_id=periodo_id, ficha_id=ficha_id, session=session
        )
        content = excel_pendientes_evaluacion(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando Excel de pendientes: {type(e).__name__}: {e}",
        )

    filename = "pendientes_evaluacion.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/exportar-sin-foto-excel",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def exportar_sin_foto_excel(session: Session = Depends(get_session)):
    """Descarga Excel de instructores que no han subido foto de perfil."""
    from fastapi.responses import Response

    try:
        from app.services.export_service import excel_instructores_sin_foto
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Falta openpyxl. En el backend ejecuta: pip install openpyxl",
        )

    try:
        data = instructores_sin_foto(session=session)
        content = excel_instructores_sin_foto(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando Excel sin foto: {type(e).__name__}: {e}",
        )

    filename = "instructores_sin_foto.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/instructor/{instructor_id}/pdf",
    dependencies=[Depends(require_roles("Administrador", "Coordinador", "Instructor"))],
)
def exportar_instructor_pdf(
    instructor_id: int,
    periodo_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """
    PDF por instructor: foto, nombre, correo, desempeño % y detalle por pregunta.
    """
    from fastapi.responses import Response
    from app.models.instructor import Instructor
    import os

    try:
        from app.services.export_service import pdf_reporte_instructor
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo cargar el generador de PDF. Instala reportlab: pip install reportlab. ({e})",
        )

    inst = session.get(Instructor, instructor_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")

    try:
        reporte = reporte_por_preguntas(
            instructor_id=instructor_id,
            periodo_id=periodo_id,
            ficha_id=None,
            session=session,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo obtener el reporte del instructor: {type(e).__name__}: {e}",
        )

    foto_path = None
    if getattr(inst, "foto", None):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        candidato = os.path.join(base, str(inst.foto).lstrip("/"))
        if os.path.isfile(candidato):
            foto_path = candidato
        else:
            candidato2 = os.path.join(base, "app", "uploads", os.path.basename(str(inst.foto)))
            if os.path.isfile(candidato2):
                foto_path = candidato2
            else:
                candidato3 = os.path.join(base, "uploads", os.path.basename(str(inst.foto)))
                if os.path.isfile(candidato3):
                    foto_path = candidato3

    rol = getattr(inst, "planta_contrato", None) or "Instructor"
    data = {
        "nombre": inst.nombre,
        "apellido": inst.apellido,
        "correo": inst.correo,
        "rol": rol,
        "foto_path": foto_path,
        "promedio_general": reporte.get("promedio_general"),
        "porcentaje_general": reporte.get("porcentaje_general"),
        "preguntas": reporte.get("preguntas") or [],
        "total_siempre": reporte.get("total_siempre"),
        "total_algunas": reporte.get("total_algunas"),
        "total_nunca": reporte.get("total_nunca"),
        "total_respuestas": reporte.get("total_respuestas"),
        "total_preguntas": reporte.get("total_preguntas"),
        "aprendices_evaluaron": reporte.get("aprendices_evaluaron"),
        "observaciones": reporte.get("observaciones") or [],
        "periodo": None,
    }
    if periodo_id:
        from app.models.periodo import Periodo
        per = session.get(Periodo, periodo_id)
        if per:
            data["periodo"] = getattr(per, "nombre", None)
    try:
        content = pdf_reporte_instructor(data)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Falta la librería reportlab. En el backend ejecuta: pip install reportlab",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando PDF: {type(e).__name__}: {e}",
        )

    safe_name = f"reporte_instructor_{instructor_id}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


# ── Consolidado evaluación (estilo reporte SENA) ─────────────────────────────

@router.get(
    "/exportar-consolidado-excel",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def exportar_consolidado_excel(
    periodo_id: Optional[int] = Query(None),
    ficha_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
):
    """
    Descarga Excel consolidado de evaluación de instructores
    (hoja GENERAL + una hoja por instructor con Siempre/Algunas/Nunca).
    """
    from fastapi.responses import Response
    from app.services.export_service import excel_consolidado_evaluacion

    periodo = None
    if periodo_id:
        periodo = session.get(Periodo, periodo_id)
    else:
        periodo = session.exec(
            select(Periodo).where(Periodo.estado == "Activo")
        ).first()

    statement = select(Evaluacion).where(Evaluacion.estado == "Evaluado")
    if periodo:
        statement = statement.where(Evaluacion.id_periodo == periodo.id_periodo)
    if ficha_id:
        statement = statement.join(Aprendiz).where(Aprendiz.id_ficha == ficha_id)
    evaluaciones = session.exec(statement).all()
    ids_eval = [e.id_evaluacion for e in evaluaciones]

    if not ids_eval:
        data = {
            "titulo": "CONSOLIDADO GENERAL EVALUACIÓN INSTRUCTORES",
            "periodo_nombre": getattr(periodo, "nombre", "") if periodo else "",
            "fecha_aplicacion": "",
            "instructores": [],
        }
        content = excel_consolidado_evaluacion(data)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="consolidado_evaluacion.xlsx"'
            },
        )

    respuestas = session.exec(
        select(Respuesta).where(Respuesta.id_evaluacion.in_(ids_eval))
    ).all()
    preguntas = {p.id_pregunta: p for p in session.exec(select(Pregunta)).all()}

    por_inst = defaultdict(
        lambda: {
            "por_pregunta": defaultdict(lambda: {5: 0, 3: 0, 1: 0}),
            "aprendices": set(),
            "obs": [],
            "total_s": 0,
            "total_a": 0,
            "total_n": 0,
            "total_r": 0,
        }
    )

    eval_to_aprendiz = {e.id_evaluacion: e.id_aprendiz for e in evaluaciones}

    for r in respuestas:
        d = por_inst[r.id_instructor]
        val = r.respuesta
        if val >= 4:
            bucket = 5
        elif val >= 2:
            bucket = 3
        else:
            bucket = 1
        d["por_pregunta"][r.id_pregunta][bucket] += 1
        d["total_r"] += 1
        if bucket == 5:
            d["total_s"] += 1
        elif bucket == 3:
            d["total_a"] += 1
        else:
            d["total_n"] += 1
        ap_id = eval_to_aprendiz.get(r.id_evaluacion)
        if ap_id:
            d["aprendices"].add(ap_id)
        if r.observaciones and str(r.observaciones).strip():
            d["obs"].append(str(r.observaciones).strip())

    instructores_out = []
    for inst_id, d in por_inst.items():
        inst = session.get(Instructor, inst_id)
        nombre = (
            f"{inst.nombre} {inst.apellido}" if inst else f"Instructor #{inst_id}"
        )
        total_r = d["total_r"] or 1
        # Escala oficial: Siempre=100, Algunas=50, Nunca=0
        porcentaje = round((100 * d["total_s"] + 50 * d["total_a"] + 0 * d["total_n"]) / total_r)
        suma = 5 * d["total_s"] + 3 * d["total_a"] + 1 * d["total_n"]
        promedio = suma / total_r

        lista_preg = []
        for pid, counts in sorted(
            d["por_pregunta"].items(),
            key=lambda x: getattr(preguntas.get(x[0]), "orden", 0) or 0,
        ):
            preg = preguntas.get(pid)
            lista_preg.append(
                {
                    "orden": getattr(preg, "orden", 0) if preg else 0,
                    "enunciado": (
                        getattr(preg, "descripcion", f"Pregunta {pid}")
                        if preg
                        else f"Pregunta {pid}"
                    ),
                    "siempre": counts[5],
                    "algunas": counts[3],
                    "nunca": counts[1],
                }
            )

        instructores_out.append(
            {
                "id_instructor": inst_id,
                "nombre": nombre,
                "rol": getattr(inst, "planta_contrato", None) or "Técnico",
                "aprendices_evaluaron": len(d["aprendices"]),
                "porcentaje": porcentaje,
                "preguntas": lista_preg,
                "total_siempre": d["total_s"],
                "total_algunas": d["total_a"],
                "total_nunca": d["total_n"],
                "total_respuestas": d["total_r"],
                "observaciones": list(dict.fromkeys(d["obs"]))[:50],
            }
        )

    instructores_out.sort(key=lambda x: x["porcentaje"], reverse=True)

    fecha_apl = ""
    if (
        periodo
        and getattr(periodo, "fecha_inicio", None)
        and getattr(periodo, "fecha_fin", None)
    ):
        fecha_apl = f"{periodo.fecha_inicio} AL {periodo.fecha_fin}"

    data = {
        "titulo": "CONSOLIDADO GENERAL EVALUACIÓN INSTRUCTORES",
        "periodo_nombre": getattr(periodo, "nombre", "") if periodo else "",
        "fecha_aplicacion": fecha_apl,
        "instructores": instructores_out,
    }
    content = excel_consolidado_evaluacion(data)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="consolidado_evaluacion.xlsx"'
        },
    )
