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
    """Divide 'Adriana Maritza Vega' en nombre y apellido de forma razonable.

    1 palabra: solo nombre; 2: nombre + apellido; 3: dos nombres + apellido;
    4 o más: los dos últimos son los apellidos.
    """
    partes = (completo or "").split()
    if len(partes) < 2:
        return (partes[0] if partes else ""), ""
    corte = -2 if len(partes) >= 4 else -1
    return " ".join(partes[:corte]), " ".join(partes[corte:])


def _texto(valor) -> str:
    return str(valor).strip() if valor is not None else ""


def parsear_csv(contenido: bytes | str) -> list[dict[str, str]]:
    if isinstance(contenido, bytes):
        if contenido.startswith(b"\xef\xbb\xbf"):
            contenido = contenido[3:]
        contenido = contenido.decode("utf-8", errors="replace")

    primera = contenido.splitlines()[0] if contenido.strip() else ""
    delimiter = ";" if primera.count(";") > primera.count(",") else ","

    reader = csv.DictReader(io.StringIO(contenido), delimiter=delimiter)
    return [
        {_normalizar_cabecera(k): (v or "").strip() for k, v in row.items() if k is not None}
        for row in reader
    ]


def _fila_vacia(row) -> bool:
    return not row or all(_texto(c) == "" for c in row)


def _normalizar_celdas(headers: list[str], row) -> dict[str, str]:
    return {key: _texto(cell) for key, cell in zip(headers, row) if key}


def parsear_xlsx(contenido: bytes) -> list[dict[str, str]]:
    try:
        from openpyxl import load_workbook
    except ImportError as e:
        raise RuntimeError(
            "openpyxl no está instalado. Ejecuta: pip install openpyxl"
        ) from e

    wb = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [_normalizar_cabecera(_texto(h)) for h in rows[0]]
    filas = [_normalizar_celdas(headers, row) for row in rows[1:] if not _fila_vacia(row)]
    wb.close()
    return filas


def parsear_archivo(contenido: bytes, filename: str) -> list[dict[str, str]]:
    if (filename or "").lower().endswith((".xlsx", ".xls")):
        return parsear_xlsx(contenido)
    return parsear_csv(contenido)


def _primero(fila: dict[str, str], *claves: str) -> str:
    """Primer valor no vacío de las claves indicadas, sin espacios."""
    return next((fila.get(k) for k in claves if fila.get(k)), "").strip()


def _nombre_y_apellido(fila: dict[str, str]) -> tuple[str, str]:
    nombre_completo = _primero(fila, "nombre_completo")
    if nombre_completo:
        return _dividir_nombre_completo(nombre_completo)
    return _primero(fila, "nombre"), _primero(fila, "apellido")


def _planta_contrato(valor: str) -> str | None:
    pc_raw = valor.upper()
    if not pc_raw:
        return None
    if "PLANTA" in pc_raw:
        return "PLANTA"
    if "CONTRAT" in pc_raw:
        return "CONTRATO"
    return pc_raw[:20]


def _extraer_campos(fila: dict[str, str]) -> tuple[str, str, str, str, str | None]:
    correo = _primero(fila, "correo", "correo_electronico", "correo_sena").lower()
    nombre, apellido = _nombre_y_apellido(fila)
    telefono = _primero(fila, "telefono", "documento") or "0000000000"
    planta_contrato = _planta_contrato(_primero(fila, "planta_contrato"))
    return nombre, apellido, correo, telefono, planta_contrato


MSG_FALTAN = "Faltan nombre completo o correo institucional @sena.edu.co."
MSG_CORREO = (
    "El correo debe ser institucional (@sena.edu.co). Columna: CORREO "
    "ELECTRÓNICO @SENA.EDU.CO"
)


def _validar(nombre: str, correo: str) -> tuple[str, str] | None:
    """(correo_a_mostrar, mensaje) si la fila no es válida; None si está bien."""
    if not nombre or not correo:
        return correo or "(vacío)", MSG_FALTAN
    if not correo.endswith("@sena.edu.co"):
        return correo, MSG_CORREO
    return None


def _es_duplicado(msg: str) -> bool:
    return "ya existe" in msg.lower()


def _crear_instructor(session: Session, i: int, campos: tuple, resultado: dict) -> None:
    nombre, apellido, correo, telefono, planta_contrato = campos
    try:
        data = InstructorCreate(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            foto=None,
            planta_contrato=planta_contrato,
            resultados_aprendizaje=[],
        )
        # Correos se envían después con el botón «Enviar correos»
        inst = InstructorService.crear(session, data, enviar_correo=False)
        resultado["creados"].append({
            "fila": i,
            "correo": correo,
            "nombre": f"{nombre} {apellido}",
            "id_instructor": inst.id_instructor,
        })
    except ValueError as e:
        msg = str(e)
        if _es_duplicado(msg):
            resultado["omitidos"].append({"fila": i, "correo": correo, "motivo": msg})
        else:
            resultado["errores"].append({"fila": i, "correo": correo, "error": msg})
    except Exception as e:
        resultado["errores"].append(
            {"fila": i, "correo": correo, "error": f"{type(e).__name__}: {e}"}
        )


def cargar_desde_filas(session: Session, filas: list[dict[str, str]]) -> dict[str, Any]:
    resultado: dict[str, list] = {"creados": [], "omitidos": [], "errores": []}
    for i, fila in enumerate(filas, start=2):
        nombre, apellido, correo, telefono, planta_contrato = _extraer_campos(fila)
        invalido = _validar(nombre, correo)
        if invalido:
            resultado["errores"].append({"fila": i, "correo": invalido[0], "error": invalido[1]})
            continue
        campos = (nombre, apellido or "-", correo, telefono, planta_contrato)
        _crear_instructor(session, i, campos, resultado)

    creados, omitidos, errores = (resultado[k] for k in ("creados", "omitidos", "errores"))
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
            "No se enviaron correos: usa el botón Enviar correos en la lista de instructores."
        ),
    }
