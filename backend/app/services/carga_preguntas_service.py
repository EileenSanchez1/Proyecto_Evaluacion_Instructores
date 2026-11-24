"""
Carga de preguntas desde Excel del formato oficial SENA
(Evaluación de instructores en aula).

Se toman únicamente filas que parecen preguntas:
- Columna con número de orden (ej. 1.1, 2.3) o entero
- Columna con el texto de la afirmación / pregunta

Formato esperado (flexible):
  | orden | descripcion |
  | 1.1   | El instructor es puntual... |
o el layout del formato SENA donde la primera columna es el código
y la segunda el texto.
"""
from __future__ import annotations

import io
import re
from typing import Any

from sqlmodel import Session, select

from app.models.pregunta import Pregunta


def _celda(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


# Códigos de pregunta del formato SENA (1.1, 2.4, 3.2, etc.)
CODIGO_RE = re.compile(r"^(\d+)(?:\.(\d+))?$")
# Textos de títulos / encabezados del formato oficial que no son preguntas
TITULOS_XLSX = (
    "servicio nacional",
    "evaluacion de instructores",
    "nombre instructor",
    "cordial saludo",
    "proposito de evaluar",
    "afirmaciones",
    "cumplimiento, conocimiento",
    "metodologia de formacion",
    "evaluacion aplicada",
    "clima organizacional",
)
CABECERAS_CSV = ("orden", "descripcion", "pregunta", "codigo", "afirmacion", "texto")


def _sin_espacios(texto: str) -> str:
    return texto.replace(" ", "")


def _es_codigo(texto: str) -> bool:
    return bool(CODIGO_RE.match(_sin_espacios(texto)))


def _contiene(celdas: list[str], palabras: tuple) -> bool:
    unidos = " ".join(celdas).lower()
    return any(x in unidos for x in palabras)


def _orden_desde_codigo(codigo: str, orden_auto: int) -> int:
    """1.1 -> 11, 2.4 -> 24, 3 -> 3; si no es código, el orden secuencial."""
    m = CODIGO_RE.match(_sin_espacios(codigo or ""))
    if not m:
        return orden_auto
    mayor = int(m.group(1))
    menor = int(m.group(2) or 0)
    return mayor * 10 + menor if menor else mayor


def _numerar(filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena por orden y reasigna un orden secuencial limpio 1..n."""
    filas.sort(key=lambda x: x["orden"])
    for i, f in enumerate(filas, 1):
        f["orden"] = i
    return filas


# ── Excel ────────────────────────────────────────────────────────────────────

def _codigo_en_fila(celdas: list[str]) -> tuple[str, str]:
    """Primer código de pregunta de la fila y el resto de la fila como texto."""
    for i, c in enumerate(celdas):
        if c and _es_codigo(c):
            resto = [x for j, x in enumerate(celdas) if j != i and x]
            return _sin_espacios(c), " ".join(resto).strip()
    return "", ""


def _codigo_alternativo(celdas: list[str], orden_auto: int) -> tuple[str, str]:
    """Primera columna número + segunda texto, o una fila con solo texto largo."""
    primera = celdas[0]
    if primera and len(celdas) > 1 and celdas[1]:
        if _es_codigo(primera) or primera.isdigit():
            return _sin_espacios(primera), celdas[1]
        return "", ""
    # Fila con solo texto largo (sin SI/NO headers)
    if len(primera) > 25 and "si" not in primera.lower()[:5]:
        return str(orden_auto), primera
    return "", ""


def _texto_valido(texto: str) -> bool:
    # Mínimo 15 caracteres y evitar columnas SI/NO sueltas
    return len(texto) >= 15 and texto.upper() not in ("SI", "NO", "SÍ")


def _fila_xlsx(row, orden_auto: int) -> dict[str, Any] | None:
    celdas = [_celda(c) for c in row or ()]
    if not any(celdas):
        return None
    # Título de sección (sin código de pregunta): se omite
    if _contiene(celdas, TITULOS_XLSX) and not _es_codigo(celdas[0]):
        return None
    codigo, texto = _codigo_en_fila(celdas)
    if not codigo:
        codigo, texto = _codigo_alternativo(celdas, orden_auto)
    if not _texto_valido(texto):
        return None
    return {
        "orden": _orden_desde_codigo(codigo, orden_auto),
        "descripcion": texto,
        "codigo": codigo,
    }


def parsear_xlsx_preguntas(contenido: bytes) -> list[dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as e:
        raise RuntimeError(
            "openpyxl no está instalado. Ejecuta: pip install openpyxl"
        ) from e

    wb = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    filas: list[dict[str, Any]] = []
    for row in wb.active.iter_rows(values_only=True):
        fila = _fila_xlsx(row, len(filas) + 1)
        if fila:
            filas.append(fila)
    wb.close()
    return _numerar(filas)


# ── CSV ──────────────────────────────────────────────────────────────────────

def _delimitador(texto: str) -> str:
    """Separador tab, punto y coma o coma según la primera línea."""
    primera = texto.splitlines()[0] if texto.strip() else ""
    for delim in ("\t", ";"):
        if delim in primera:
            return delim
    return ","


def _codigo_texto_csv(celdas: list[str]) -> tuple[str, str]:
    codigo = texto = ""
    for c in celdas:
        if not c:
            continue
        if not codigo and _es_codigo(c):
            codigo = c
            continue
        if len(c) >= 10:
            texto = c
            break
    if not texto and len(celdas) >= 2:
        texto = celdas[1] if len(celdas[1]) >= 5 else celdas[-1]
    return codigo, texto


def _fila_csv(celdas: list[str], orden_auto: int) -> dict[str, Any] | None:
    codigo, texto = _codigo_texto_csv(celdas)
    if len(texto) < 10:
        return None
    return {
        "orden": _orden_desde_codigo(codigo, orden_auto),
        "descripcion": texto,
        "codigo": codigo,
    }


def parsear_csv_preguntas(contenido: bytes) -> list[dict[str, Any]]:
    """
    Parsea CSV/TSV simple con columnas orden,descripcion o codigo,texto.
    Acepta separador coma o punto y coma o tab.
    """
    import csv

    texto = contenido.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(texto), delimiter=_delimitador(texto))
    filas: list[dict[str, Any]] = []
    primera_fila = True
    for row in reader:
        celdas = [c.strip() for c in row]
        if not any(celdas):
            continue
        # Solo la primera fila con datos puede ser el encabezado
        es_cabecera = primera_fila and _contiene(celdas, CABECERAS_CSV)
        primera_fila = False
        if es_cabecera:
            continue
        fila = _fila_csv(celdas, len(filas) + 1)
        if fila:
            filas.append(fila)
    return _numerar(filas)


def cargar_preguntas_desde_filas(
    session: Session,
    filas: list[dict[str, Any]],
    reemplazar: bool = False,
) -> dict[str, Any]:
    if reemplazar:
        existentes = session.exec(select(Pregunta)).all()
        for p in existentes:
            p.estado = False
            session.add(p)
        session.commit()

    creadas = 0
    actualizadas = 0
    omitidas = 0

    for item in filas:
        desc = (item.get("descripcion") or "").strip()
        orden = int(item.get("orden") or 0)
        if not desc:
            continue
        ya = session.exec(select(Pregunta).where(Pregunta.descripcion == desc)).first()
        if ya:
            if reemplazar:
                ya.estado = True
                ya.orden = orden
                session.add(ya)
                actualizadas += 1
            else:
                omitidas += 1
            continue
        session.add(Pregunta(descripcion=desc, orden=orden, estado=True))
        creadas += 1

    session.commit()
    return {
        "mensaje": (
            f"Preguntas desde Excel: {creadas} creadas, {actualizadas} actualizadas, {omitidas} "
            "omitidas."
        ),
        "creadas": creadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas,
        "total_en_archivo": len(filas),
        "reemplazar": reemplazar,
    }
