"""
Generación de reportes en Excel (.xlsx): pendientes de evaluación, instructores
sin foto de perfil y consolidado de evaluación. El PDF está en export_pdf_service.py.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def _estilo_cabecera(ws, row: int, cols: int):
    fill = PatternFill("solid", fgColor="39A900")
    font = Font(bold=True, color="FFFFFF")
    thin = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin


def _auto_ancho(ws, max_width: int = 45):
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        length = 0
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            length = max(length, min(len(val), max_width))
        ws.column_dimensions[letter].width = max(12, length + 2)


def _titulo(ws, texto: str, rango: str) -> None:
    ws["A1"] = texto
    ws["A1"].font = Font(bold=True, size=14, color="1F2937")
    ws.merge_cells(rango)


def _subtitulo(ws, texto: str, rango: str) -> None:
    ws["A2"] = texto
    ws["A2"].font = Font(color="6B7280", size=10)
    ws.merge_cells(rango)


def _cabeceras(ws, row: int, headers: list) -> None:
    for i, h in enumerate(headers, 1):
        ws.cell(row=row, column=i, value=h)
    _estilo_cabecera(ws, row, len(headers))


def _escribir_filas(ws, filas: list, inicio: int = 5) -> int:
    """Escribe una lista de filas desde `inicio`. Devuelve cuántas escribió."""
    for r, valores in enumerate(filas, inicio):
        for c, valor in enumerate(valores, 1):
            ws.cell(row=r, column=c, value=valor)
    return len(filas)


def _a_bytes(wb) -> bytes:
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _fila_pendiente(p: dict) -> list:
    nombres_inst = ", ".join(
        i.get("nombre", "") for i in (p.get("instructores_pendientes") or [])
    )
    return [
        p.get("ficha") or p.get("numero_ficha") or "",
        p.get("nombre") or "",
        p.get("documento") or "",
        p.get("correo") or "",
        nombres_inst,
        p.get("total_pendientes") or 0,
    ]


def excel_pendientes_evaluacion(data: dict[str, Any]) -> bytes:
    """
    data: respuesta de pendientes_evaluacion
    columnas: Ficha, Aprendiz, Documento, Correo, Instructores pendientes, Total pendientes
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Pendientes evaluación"
    _titulo(ws, "Reporte de aprendices con evaluaciones pendientes", "A1:F1")
    _subtitulo(ws, f"Periodo ID: {data.get('periodo_id') or '—'}  |  Generado: {_ahora()}", "A2:F2")
    _cabeceras(ws, 4, [
        "Ficha", "Aprendiz", "Documento", "Correo", "Instructores pendientes", "Total pendientes",
    ])
    filas = [_fila_pendiente(p) for p in data.get("pendientes") or []]
    if not _escribir_filas(ws, filas):
        ws.cell(row=5, column=1, value="No hay pendientes en el filtro actual.")
        ws.merge_cells("A5:F5")
    _auto_ancho(ws)
    return _a_bytes(wb)


def _fila_sin_foto(inst: dict) -> list:
    return [
        inst.get("id_instructor"),
        inst.get("nombre") or "",
        inst.get("correo") or "",
        inst.get("telefono") or "",
        "Sí" if inst.get("tiene_usuario") else "No",
    ]


def excel_instructores_sin_foto(data: dict[str, Any]) -> bytes:
    """data: respuesta de instructores_sin_foto"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Sin foto de perfil"
    _titulo(ws, "Instructores sin foto de perfil", "A1:E1")
    _subtitulo(ws, f"Generado: {_ahora()}  |  Total: {data.get('total', 0)}", "A2:E2")
    _cabeceras(ws, 4, ["ID", "Nombre", "Correo institucional", "Teléfono", "Tiene usuario"])
    filas = [_fila_sin_foto(inst) for inst in data.get("instructores") or []]
    if not _escribir_filas(ws, filas):
        ws.cell(row=5, column=1, value="Todos los instructores tienen foto de perfil.")
        ws.merge_cells("A5:E5")
    _auto_ancho(ws)
    return _a_bytes(wb)


# ── consolidado ──────────────────────────────────────────────────────────────

FILL_SECCION = PatternFill("solid", fgColor="E8F5E9")
CATEGORIAS = [("Siempre", "siempre"), ("Algunas Veces", "algunas"), ("Nunca", "nunca")]
TITULOS_CONSOLIDADO = [
    "Total Aprendices", "Total Preguntas", "Total Respuestas", "Siempre",
    "Algunas Veces", "Nunca", "Promedio Instructor",
]


def _porcentaje_texto(pct) -> str:
    return f"{pct} %" if pct is not None else "—"


def _fecha_aplicacion(data: dict) -> str:
    return f"FECHA APLICACIÓN {data.get('fecha_aplicacion') or '—'}"


def _hoja_general(ws, data: dict) -> None:
    ws.title = "GENERAL"
    ws["A1"] = data.get("titulo") or "CONSOLIDADO GENERAL EVALUACIÓN INSTRUCTORES"
    ws["A1"].font = Font(bold=True, size=14, color="1F2937")
    ws.merge_cells("A1:E1")
    ws["A2"] = data.get("periodo_nombre") or ""
    ws["D2"] = _fecha_aplicacion(data)
    ws["D2"].font = Font(size=10, color="6B7280")
    _cabeceras(ws, 4, ["INSTRUCTOR", "ROL", "APRENDICES QUE EVALUARON", "PROMEDIO"])
    filas = [
        [
            inst.get("nombre") or "",
            inst.get("rol") or "Técnico",
            inst.get("aprendices_evaluaron") or 0,
            _porcentaje_texto(inst.get("porcentaje")),
        ]
        for inst in data.get("instructores") or []
    ]
    if not _escribir_filas(ws, filas):
        ws.cell(row=5, column=1, value="Sin datos de evaluación.")
    _auto_ancho(ws)


def _nombre_hoja(wb, nombre: str) -> str:
    """Nombre válido y único para la hoja (máx. 31 caracteres en Excel)."""
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in nombre)[:28] or "Inst"
    base, n = safe, 1
    while safe in wb.sheetnames:
        safe = f"{base[:25]}_{n}"
        n += 1
    return safe


def _celda_seccion(wsi, row: int, col: int, valor: str) -> None:
    cell = wsi.cell(row=row, column=col, value=valor)
    cell.font = Font(bold=True)
    cell.fill = FILL_SECCION


def _etiqueta_pregunta(p: dict) -> str:
    orden = p.get("orden")
    enunciado = p.get("enunciado") or ""
    return f"{orden}.{enunciado}" if orden else enunciado


def _bloque_conteos(wsi, inst: dict, r: int) -> int:
    """Tabla Pregunta/conteo para Siempre, Algunas Veces y Nunca. Devuelve la fila siguiente."""
    for etiqueta, key in CATEGORIAS:
        _celda_seccion(wsi, r, 1, "Pregunta")
        _celda_seccion(wsi, r, 2, etiqueta)
        filas = [[_etiqueta_pregunta(p), p.get(key) or 0] for p in inst.get("preguntas") or []]
        r += 1 + _escribir_filas(wsi, filas, r + 1) + 1
    return r


def _bloque_consolidado(wsi, inst: dict, r: int) -> int:
    wsi.cell(row=r, column=1, value="CONSOLIDADO EVALUACIÓN").font = Font(bold=True, size=11)
    _cabeceras(wsi, r + 1, TITULOS_CONSOLIDADO)
    _escribir_filas(wsi, [[
        inst.get("aprendices_evaluaron") or 0,
        len(inst.get("preguntas") or []),
        inst.get("total_respuestas") or 0,
        inst.get("total_siempre") or 0,
        inst.get("total_algunas") or 0,
        inst.get("total_nunca") or 0,
        _porcentaje_texto(inst.get("porcentaje")),
    ]], r + 2)
    return r + 2


def _bloque_observaciones(wsi, inst: dict, r: int) -> None:
    wsi.cell(row=r, column=1, value="OBSERVACIONES").font = Font(bold=True)
    obs = inst.get("observaciones") or []
    if not obs:
        wsi.cell(row=r + 1, column=1, value="Ninguna")
        return
    textos = [[str(o).strip()] for o in obs if o and str(o).strip()]
    _escribir_filas(wsi, textos, r + 1)


def _hoja_instructor(wb, data: dict, inst: dict) -> None:
    nombre = (inst.get("nombre") or "Instructor").strip()
    wsi = wb.create_sheet(title=_nombre_hoja(wb, nombre))
    wsi["A1"] = data.get("titulo") or "REPORTE EVALUACIÓN INSTRUCTORES"
    wsi["A1"].font = Font(bold=True, size=12)
    wsi["A2"] = data.get("periodo_nombre") or ""
    wsi["C2"] = _fecha_aplicacion(data)
    wsi["A3"] = f"INSTRUCTOR {nombre}"
    wsi["A3"].font = Font(bold=True)
    wsi["C3"] = f"ROL {inst.get('rol') or 'Técnico'}"

    r = _bloque_conteos(wsi, inst, 5)
    r = _bloque_consolidado(wsi, inst, r + 1)
    _bloque_observaciones(wsi, inst, r + 2)
    _auto_ancho(wsi)


def excel_consolidado_evaluacion(data: dict) -> bytes:
    """
    Excel estilo reporte SENA de referencia:
    - Hoja GENERAL con instructor / rol / aprendices / promedio %
    - Una hoja por instructor con conteos Siempre / Algunas veces / Nunca
    """
    wb = Workbook()
    _hoja_general(wb.active, data)
    for inst in data.get("instructores") or []:
        _hoja_instructor(wb, data, inst)
    return _a_bytes(wb)
