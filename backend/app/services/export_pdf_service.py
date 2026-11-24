"""PDF individual de resultados del instructor (estilo reporte coordinación SENA).

Contenido: encabezado, datos del instructor, tabla por pregunta con conteos
Siempre / Algunas veces / Nunca y %, consolidado y observaciones.
Escala: Siempre=100%, Algunas veces=50%, Nunca=0%.
"""
import io
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

VERDE_OSCURO = colors.HexColor("#1a4a2e")
GRIS_BORDE = colors.HexColor("#d1d5db")


def _estilos() -> dict:
    base = getSampleStyleSheet()
    normal = base["Normal"]
    return {
        "titulo": ParagraphStyle(
            "TitleSENA", parent=base["Heading1"], fontSize=15, textColor=VERDE_OSCURO,
            alignment=TA_CENTER, spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "SubSENA", parent=normal, fontSize=9, textColor=colors.HexColor("#4b5563"),
            alignment=TA_CENTER, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2SENA", parent=base["Heading2"], fontSize=11, textColor=VERDE_OSCURO,
            spaceBefore=8, spaceAfter=4,
        ),
        "body": ParagraphStyle("BodySENA", parent=normal, fontSize=8, leading=11),
        "small": ParagraphStyle(
            "SmallSENA", parent=normal, fontSize=7.5, leading=10,
            textColor=colors.HexColor("#374151"),
        ),
        # Texto blanco para encabezados de tabla (sobre fondo verde oscuro)
        "header_cell": ParagraphStyle(
            "HeaderCellSENA", parent=normal, fontSize=8, leading=10, textColor=colors.white,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "foot": ParagraphStyle(
            "Foot", parent=normal, fontSize=7, textColor=colors.gray, alignment=TA_CENTER,
        ),
    }


def _a_float(valor, defecto=0.0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


# ── cálculos ─────────────────────────────────────────────────────────────────

def _nota_a_porcentaje(nota: float, decimales=None):
    """Convierte una nota 1-5 a porcentaje 0-100."""
    return round(((nota - 1) / 4) * 100, decimales) if nota > 0 else 0


def porcentaje_general(data: dict) -> float:
    """% general oficial; si no viene, se deriva del promedio (1-5 o ya en %)."""
    pct = data.get("porcentaje_general")
    if pct is None:
        prom = data.get("promedio_general")
        prom_f = _a_float(prom, None) if prom is not None else None
        if prom_f is None or prom_f <= 0:
            pct = 0
        elif prom_f > 5:
            pct = round(prom_f)
        else:
            pct = _nota_a_porcentaje(prom_f)
    return _a_float(pct)


def _conteos(p: dict) -> tuple:
    return tuple(int(p.get(k) or 0) for k in ("siempre", "algunas", "nunca"))


def porcentaje_pregunta(p: dict) -> float:
    s, a, n = _conteos(p)
    tot = s + a + n
    if tot > 0:
        return round((s * 100 + a * 50) / tot, 1)
    if p.get("porcentaje") is not None:
        return _a_float(p.get("porcentaje") or 0)
    # fallback desde nota 5/3/1
    nota = p.get("nota") if p.get("nota") is not None else p.get("promedio") or 0
    return _nota_a_porcentaje(_a_float(nota), 1)


def _descripcion(p: dict) -> str:
    claves = ("pregunta", "texto_pregunta", "descripcion", "enunciado")
    return next((p.get(k) for k in claves if p.get(k)), "—")


def _entero(data: dict, clave: str, defecto: int = 0) -> int:
    return int(data.get(clave) or defecto)


def totales(data: dict, preguntas: list) -> dict:
    """Totales del consolidado; si no vienen, se suman desde las preguntas."""
    s, a, n = (_entero(data, k) for k in ("total_siempre", "total_algunas", "total_nunca"))
    total_r = _entero(data, "total_respuestas", s + a + n)
    if total_r and not (s or a or n):
        s, a, n = (sum(_conteos(p)[i] for p in preguntas) for i in range(3))
        total_r = s + a + n or total_r
    return {
        "aprendices": _entero(data, "aprendices_evaluaron"),
        "preguntas": _entero(data, "total_preguntas", len(preguntas)),
        "respuestas": total_r,
        "siempre": s,
        "algunas": a,
        "nunca": n,
    }


# ── bloques del documento ────────────────────────────────────────────────────

def _encabezado(data: dict, st: dict) -> list:
    bloques = [
        Paragraph("SENA — Evaluación de Instructores", st["titulo"]),
        Paragraph("Reporte individual de resultados (coordinación)", st["sub"]),
    ]
    periodo = data.get("periodo") or data.get("nombre_periodo")
    if periodo:
        bloques.append(Paragraph(f"Periodo: <b>{periodo}</b>", st["sub"]))
    bloques.append(
        HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#2d7a4f"), spaceAfter=10)
    )
    return bloques


def _foto(ruta):
    """Image de reportlab o None si no hay foto válida."""
    if not (ruta and os.path.isfile(ruta)):
        return None
    try:
        return Image(ruta, width=2 * cm, height=2 * cm)
    except Exception:
        return None


def _tarjeta_instructor(data: dict, st: dict) -> Table:
    nombre = f"{data.get('nombre') or ''} {data.get('apellido') or ''}".strip() or "Instructor"
    correo = data.get("correo") or "—"
    rol = data.get("rol") or "—"
    texto = Paragraph(
        f"<b>{nombre}</b><br/>{correo}<br/><font size='8'>Rol: {rol}</font>", st["body"]
    )
    img = _foto(data.get("foto_path"))
    if img is not None:
        tabla = Table([[img, texto]], colWidths=[2.4 * cm, 14.5 * cm])
    else:
        tabla = Table([[texto]], colWidths=[16.9 * cm])
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tabla


def _cabecera(titulos: list, st: dict) -> list:
    return [Paragraph(t, st["header_cell"]) for t in titulos]


def _tabla_preguntas(preguntas: list, st: dict) -> list:
    if not preguntas:
        return [Paragraph("No hay respuestas registradas para este instructor.", st["body"])]
    rows = [_cabecera(["#", "Pregunta", "Siempre", "Algunas", "Nunca", "%"], st)]
    for p in preguntas:
        s, a, n = _conteos(p)
        rows.append([
            str(p.get("orden") or ""),
            Paragraph(str(_descripcion(p)), st["small"]),
            str(s), str(a), str(n),
            f"{porcentaje_pregunta(p):.0f}%",
        ])
    tabla = Table(
        rows,
        colWidths=[1 * cm, 9.2 * cm, 1.7 * cm, 1.7 * cm, 1.5 * cm, 1.4 * cm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.35, GRIS_BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [tabla]


def _tabla_consolidado(t: dict, pct_g: float, st: dict) -> Table:
    titulos = ["Aprendices", "Preguntas", "Respuestas", "Siempre", "Algunas", "Nunca", "Promedio"]
    valores = [
        str(t[k]) for k in ("aprendices", "preguntas", "respuestas", "siempre", "algunas", "nunca")
    ] + [f"{pct_g:.0f}%"]
    tabla = Table(
        [_cabecera(titulos, st), valores],
        colWidths=[2.2 * cm, 2.2 * cm, 2.4 * cm, 2.2 * cm, 2.2 * cm, 2 * cm, 2.2 * cm],
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, GRIS_BORDE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ecfdf5")),
        ("FONTNAME", (6, 1), (6, 1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tabla


def _observaciones(obs: list, st: dict) -> list:
    if not obs:
        return [Paragraph("Ninguna observación registrada.", st["body"])]
    bloques = []
    for txt in (str(o).strip() for o in obs[:40]):
        if txt:
            bloques += [Paragraph(f"• {txt}", st["small"]), Spacer(1, 2)]
    return bloques


def pdf_reporte_instructor(data: dict) -> bytes:
    st = _estilos()
    preguntas = data.get("preguntas") or []
    pct_g = porcentaje_general(data)

    story = _encabezado(data, st)
    story += [_tarjeta_instructor(data, st), Spacer(1, 8)]
    story.append(Paragraph(
        f"<b>Desempeño general: {pct_g:.0f}%</b> "
        f"(Siempre = 100% · Algunas veces = 50% · Nunca = 0%)",
        st["h2"],
    ))
    story.append(Paragraph("Detalle por pregunta", st["h2"]))
    story += _tabla_preguntas(preguntas, st)
    story += [Spacer(1, 10), Paragraph("Consolidado de evaluación", st["h2"])]
    story.append(_tabla_consolidado(totales(data, preguntas), pct_g, st))
    story += [Spacer(1, 10), Paragraph("Observaciones de aprendices", st["h2"])]
    story += _observaciones(data.get("observaciones") or [], st)
    story += [Spacer(1, 14), Paragraph(
        "Documento generado automáticamente por el sistema de Evaluación de Instructores SENA.",
        st["foot"],
    )]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter, leftMargin=1.4 * cm, rightMargin=1.4 * cm,
        topMargin=1.2 * cm, bottomMargin=1.2 * cm,
    )
    doc.build(story)
    return buf.getvalue()
