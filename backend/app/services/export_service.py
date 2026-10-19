"""
Generación de reportes en Excel (.xlsx) para pendientes de evaluación
e instructores sin foto de perfil.
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


def excel_pendientes_evaluacion(data: dict[str, Any]) -> bytes:
    """
    data: respuesta de pendientes_evaluacion
    columnas: Ficha, Aprendiz, Documento, Correo, Instructores pendientes, Total pendientes
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Pendientes evaluación"

    ws["A1"] = "Reporte de aprendices con evaluaciones pendientes"
    ws["A1"].font = Font(bold=True, size=14, color="1F2937")
    ws.merge_cells("A1:F1")
    ws["A2"] = f"Periodo ID: {data.get('periodo_id') or '—'}  |  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ws["A2"].font = Font(color="6B7280", size=10)
    ws.merge_cells("A2:F2")

    headers = [
        "Ficha",
        "Aprendiz",
        "Documento",
        "Correo",
        "Instructores pendientes",
        "Total pendientes",
    ]
    for i, h in enumerate(headers, 1):
        ws.cell(row=4, column=i, value=h)
    _estilo_cabecera(ws, 4, len(headers))

    row = 5
    for p in data.get("pendientes") or []:
        nombres_inst = ", ".join(
            i.get("nombre", "") for i in (p.get("instructores_pendientes") or [])
        )
        ws.cell(row=row, column=1, value=p.get("ficha") or p.get("numero_ficha") or "")
        ws.cell(row=row, column=2, value=p.get("nombre") or "")
        ws.cell(row=row, column=3, value=p.get("documento") or "")
        ws.cell(row=row, column=4, value=p.get("correo") or "")
        ws.cell(row=row, column=5, value=nombres_inst)
        ws.cell(row=row, column=6, value=p.get("total_pendientes") or 0)
        row += 1

    if row == 5:
        ws.cell(row=5, column=1, value="No hay pendientes en el filtro actual.")
        ws.merge_cells("A5:F5")

    _auto_ancho(ws)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def excel_instructores_sin_foto(data: dict[str, Any]) -> bytes:
    """data: respuesta de instructores_sin_foto"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Sin foto de perfil"

    ws["A1"] = "Instructores sin foto de perfil"
    ws["A1"].font = Font(bold=True, size=14, color="1F2937")
    ws.merge_cells("A1:E1")
    ws["A2"] = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  Total: {data.get('total', 0)}"
    ws["A2"].font = Font(color="6B7280", size=10)
    ws.merge_cells("A2:E2")

    headers = ["ID", "Nombre", "Correo institucional", "Teléfono", "Tiene usuario"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=4, column=i, value=h)
    _estilo_cabecera(ws, 4, len(headers))

    row = 5
    for inst in data.get("instructores") or []:
        ws.cell(row=row, column=1, value=inst.get("id_instructor"))
        ws.cell(row=row, column=2, value=inst.get("nombre") or "")
        ws.cell(row=row, column=3, value=inst.get("correo") or "")
        ws.cell(row=row, column=4, value=inst.get("telefono") or "")
        ws.cell(row=row, column=5, value="Sí" if inst.get("tiene_usuario") else "No")
        row += 1

    if row == 5:
        ws.cell(row=5, column=1, value="Todos los instructores tienen foto de perfil.")
        ws.merge_cells("A5:E5")

    _auto_ancho(ws)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
