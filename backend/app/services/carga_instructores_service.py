"""
Carga masiva de instructores desde CSV o Excel (.xlsx) sin foto.

Formato oficial (Excel de planta SENA):

  NOMBRES Y APELLIDOS COMPLETOS | NUMERO DOCUMENTO | PLANTA / CONTRATO |
  CORREO ELECTRÓNICO PERSONAL | CORREO ELECTRÓNICO @SENA.EDU.CO

También se acepta el formato antiguo CSV:
  nombre,apellido,correo,telefono

La foto la sube el instructor al entrar (perfil / primer acceso).
Cada fila crea instructor + usuario en modo primer acceso.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Any

from sqlmodel import Session

from app.schemas.instructor import InstructorCreate
from app.services.instructor_service import InstructorService
from app.services.email_service import enviar_invitacion_instructor


def _normalizar_cabecera(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    n = (
        n.replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )
    n = re.sub(r"[^a-z0-9_]", "", n)

    alias = {
        "email": "correo",
        "mail": "correo",
        "e_mail": "correo",
        "correo_electronico": "correo",
        "correo_electronico_personal": "correo_personal",
        "correo_electronico_senaeduco": "correo",
        "correo_electronico_sena": "correo",
        "correo_sena": "correo",
        "correoelectronico": "correo",
        "nombres": "nombre",
        "apellidos": "apellido",
        "nombres_y_apellidos_completos": "nombre_completo",
        "nombresyapellidoscompletos": "nombre_completo",
        "nombre_completo": "nombre_completo",
        "numero_documento": "documento",
        "numerodocumento": "documento",
        "documento": "documento",
        "cedula": "documento",
        "planta_contrato": "planta_contrato",
        "plantacontrato": "planta_contrato",
        "planta": "planta_contrato",
        "contrato": "planta_contrato",
        "celular": "telefono",
        "tel": "telefono",
        "telefono": "telefono",
        "phone": "telefono",
    }
    return alias.get(n, n)


def _dividir_nombre_completo(completo: str) -> tuple[str, str]:
    """Divide 'Adriana Maritza Vega' en nombre y apellido de forma razonable."""
    partes = [p for p in (completo or "").strip().split() if p]
    if not partes:
        return "", ""
    if len(partes) == 1:
        return partes[0], ""
    if len(partes) == 2:
        return partes[0], partes[1]
    if len(partes) >= 4:
        return " ".join(partes[:-2]), " ".join(partes[-2:])
    return " ".join(partes[:-1]), partes[-1]


def parsear_csv(contenido: bytes | str) -> list[dict[str, str]]:
    if isinstance(contenido, bytes):
        if contenido.startswith(b"\xef\xbb\xbf"):
            contenido = contenido[3:]
        texto = contenido.decode("utf-8", errors="replace")
    else:
        texto = contenido

    primera = texto.splitlines()[0] if texto.strip() else ""
    delimiter = ";" if primera.count(";") > primera.count(",") else ","

    reader = csv.DictReader(io.StringIO(texto), delimiter=delimiter)
    filas: list[dict[str, str]] = []
    for row in reader:
        normalizada = {}
        for k, v in row.items():
            if k is None:
                continue
            key = _normalizar_cabecera(k)
            normalizada[key] = (v or "").strip()
        filas.append(normalizada)
    return filas


def parsear_xlsx(contenido: bytes) -> list[dict[str, str]]:
    try:
        from openpyxl import load_workbook
    except ImportError as e:
        raise RuntimeError(
            "openpyxl no está instalado. Ejecuta: pip install openpyxl"
        ) from e

    wb = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [_normalizar_cabecera(str(h) if h is not None else "") for h in rows[0]]
    filas: list[dict[str, str]] = []

    for row in rows[1:]:
        if not row or all(c is None or str(c).strip() == "" for c in row):
            continue
        normalizada: dict[str, str] = {}
        for i, cell in enumerate(row):
            if i >= len(headers):
                break
            key = headers[i]
            if not key:
                continue
            normalizada[key] = (str(cell).strip() if cell is not None else "")
        filas.append(normalizada)

    wb.close()
    return filas


def parsear_archivo(contenido: bytes, filename: str) -> list[dict[str, str]]:
    nombre = (filename or "").lower()
    if nombre.endswith(".xlsx") or nombre.endswith(".xls"):
        return parsear_xlsx(contenido)
    return parsear_csv(contenido)


def _extraer_campos(fila: dict[str, str]) -> tuple[str, str, str, str]:
    """Devuelve (nombre, apellido, correo, telefono)."""
    correo = (
        fila.get("correo")
        or fila.get("correo_sena")
        or ""
    ).strip().lower()

    nombre_completo = (fila.get("nombre_completo") or "").strip()
    if nombre_completo:
        nombre, apellido = _dividir_nombre_completo(nombre_completo)
    else:
        nombre = (fila.get("nombre") or "").strip()
        apellido = (fila.get("apellido") or "").strip()

    telefono = (fila.get("telefono") or fila.get("documento") or "").strip() or "0000000000"

    return nombre, apellido, correo, telefono


def cargar_desde_filas(session: Session, filas: list[dict[str, str]]) -> dict[str, Any]:
    creados = []
    omitidos = []
    errores = []

    for i, fila in enumerate(filas, start=2):
        nombre, apellido, correo, telefono = _extraer_campos(fila)

        if not nombre or not correo:
            errores.append({
                "fila": i,
                "correo": correo or "(vacío)",
                "error": "Faltan nombre completo o correo institucional @sena.edu.co.",
            })
            continue

        if not apellido:
            apellido = "-"

        if not correo.endswith("@sena.edu.co"):
            errores.append({
                "fila": i,
                "correo": correo,
                "error": "El correo debe ser institucional (@sena.edu.co). Columna: CORREO ELECTRÓNICO @SENA.EDU.CO",
            })
            continue

        try:
            data = InstructorCreate(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                foto=None,
                resultados_aprendizaje=[],
            )
            inst = InstructorService.crear(session, data)

            try:
                enviar_invitacion_instructor(
                    destinatario=correo,
                    nombre=f"{nombre} {apellido}",
                    plazo_horas=48,
                )
            except Exception as e:
                print(f"[EMAIL] No se pudo enviar invitación a {correo}: {e}")

            creados.append({
                "fila": i,
                "correo": correo,
                "nombre": f"{nombre} {apellido}",
                "id_instructor": inst.id_instructor,
            })
        except ValueError as e:
            msg = str(e)
            if "Ya existe" in msg or "ya existe" in msg.lower():
                omitidos.append({
                    "fila": i,
                    "correo": correo,
                    "motivo": msg,
                })
            else:
                errores.append({
                    "fila": i,
                    "correo": correo,
                    "error": msg,
                })
        except Exception as e:
            errores.append({
                "fila": i,
                "correo": correo,
                "error": f"{type(e).__name__}: {e}",
            })

    return {
        "total_filas": len(filas),
        "creados": len(creados),
        "omitidos": len(omitidos),
        "errores": len(errores),
        "detalle_creados": creados,
        "detalle_omitidos": omitidos,
        "detalle_errores": errores,
        "mensaje": (
            f"Proceso terminado: {len(creados)} creados, "
            f"{len(omitidos)} omitidos (ya existían), "
            f"{len(errores)} con error. "
            "Sin foto: cada instructor la sube al iniciar sesión en su perfil. "
            "Se envió correo de bienvenida a los nuevos."
        ),
    }
