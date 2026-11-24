"""
Carga masiva de aprendices desde CSV o Excel (.xlsx / .xls).

Formato oficial SENA — «Reporte de Aprendices»:

  (filas superiores pueden traer título y metadatos)
  Ficha de Caracterización: 3171690 - PRODUCCION DE MULTIMEDIA
  ...
  Tipo de Documento | Número de Documento | Nombre | Apellidos |
  Celular | Correo Electrónico | Estado

También se acepta el formato simple CSV:
  nombre,apellido,correo,numero_ficha

Cada fila:
  - Crea aprendiz + usuario ya asignado a la ficha
  - Genera contraseña temporal
  - Envía correo con usuario/contraseña (cartero)
"""

from __future__ import annotations

import csv
import io
import os
import re
import subprocess
import tempfile
from typing import Any

from sqlmodel import Session, select

from app.models.ficha import Ficha
from app.schemas.aprendiz import AprendizCreate
from app.services.aprendiz_service import AprendizService


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
        "correoelectronico": "correo",
        "ficha": "numero_ficha",
        "n_ficha": "numero_ficha",
        "num_ficha": "numero_ficha",
        "numero_ficha": "numero_ficha",
        "nombres": "nombre",
        "nombre": "nombre",
        "apellidos": "apellido",
        "apellido": "apellido",
        "periodo": "id_periodo",
        "idperiodo": "id_periodo",
        "tipo_de_documento": "tipo_documento",
        "tipodedocumento": "tipo_documento",
        "numero_de_documento": "documento",
        "numerodedocumento": "documento",
        "numero_documento": "documento",
        "documento": "documento",
        "cedula": "documento",
        "celular": "celular",
        "telefono": "celular",
        "tel": "celular",
        "estado": "estado",
    }
    return alias.get(n, n)


def _extraer_numero_ficha_metadato(texto: str) -> str | None:
    """Busca 'Ficha de Caracterización: 3171690 - PROGRAMA' o similar."""
    if not texto:
        return None
    m = re.search(
        r"ficha\s*(?:de\s*caracterizaci[oó]n)?\s*[:\-]?\s*(\d{5,})",
        texto,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{6,})\b", texto)
    return m.group(1) if m else None


def _es_fila_cabecera(texto: str) -> bool:
    """True si el texto (en minúsculas) parece la fila de títulos de columnas."""
    return (
        ("nombre" in texto and ("apellido" in texto or "correo" in texto))
        or "tipo de documento" in texto
        or "correo electrónico" in texto
        or "correo electronico" in texto
    )


def _indice_cabecera(textos: list[str]) -> int:
    """Posición de la fila de títulos (0 si no se encuentra)."""
    return next((i for i, t in enumerate(textos) if _es_fila_cabecera(t.lower())), 0)


def _buscar_ficha_meta(textos) -> str | None:
    """Primer número de ficha encontrado en los textos de los metadatos."""
    for texto in textos:
        num = _extraer_numero_ficha_metadato(texto)
        if num:
            return num
    return None


def _texto(valor) -> str:
    return str(valor).strip() if valor is not None else ""


def _fila_vacia(row) -> bool:
    return not row or all(_texto(c) == "" for c in row)


def _con_ficha(normalizada: dict[str, str], ficha_meta: str | None) -> dict[str, str]:
    if ficha_meta and not normalizada.get("numero_ficha"):
        normalizada["numero_ficha"] = ficha_meta
    return normalizada


def _ficha_meta_en_celdas(rows: list[list[Any]]) -> str | None:
    return _buscar_ficha_meta(str(cell) for row in rows for cell in row if cell is not None)


def _texto_fila(row) -> str:
    return " ".join(_texto(c).lower() for c in row)


def _normalizar_celdas(headers: list[str], row) -> dict[str, str]:
    return {key: _texto(cell) for key, cell in zip(headers, row) if key}


def _filas_desde_matriz(
    rows: list[list[Any]], ficha_meta: str | None = None
) -> list[dict[str, str]]:
    """Convierte matriz de celdas (lista de filas) en filas normalizadas."""
    if not rows:
        return []
    if ficha_meta is None:
        ficha_meta = _ficha_meta_en_celdas(rows[:15])
    idx_header = _indice_cabecera([_texto_fila(row) for row in rows[:40]])
    headers = [_normalizar_cabecera(_texto(h)) for h in rows[idx_header]]
    return [
        _con_ficha(_normalizar_celdas(headers, row), ficha_meta)
        for row in rows[idx_header + 1:]
        if not _fila_vacia(row)
    ]


def _decodificar(contenido: bytes | str) -> str:
    if isinstance(contenido, str):
        return contenido
    if contenido.startswith(b"\xef\xbb\xbf"):
        contenido = contenido[3:]
    return contenido.decode("utf-8", errors="replace")


def _normalizar_dict(row: dict) -> dict[str, str]:
    return {_normalizar_cabecera(k): (v or "").strip() for k, v in row.items() if k is not None}


def parsear_csv(contenido: bytes | str) -> list[dict[str, str]]:
    lineas = _decodificar(contenido).splitlines()
    ficha_meta = _buscar_ficha_meta(lineas[:15])
    idx_header = _indice_cabecera(lineas[:30])

    texto_util = "\n".join(lineas[idx_header:])
    primera = texto_util.splitlines()[0] if texto_util.strip() else ""
    delimiter = ";" if primera.count(";") > primera.count(",") else ","

    reader = csv.DictReader(io.StringIO(texto_util), delimiter=delimiter)
    return [_con_ficha(_normalizar_dict(row), ficha_meta) for row in reader]


def parsear_xlsx_bytes(contenido: bytes) -> list[dict[str, str]]:
    from openpyxl import load_workbook

    wb = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    ws = wb.active
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    wb.close()
    return _filas_desde_matriz(rows)


def _es_html(contenido: bytes) -> bool:
    head = contenido[:2000].lstrip().lower()
    return head.startswith(b"<html") or head.startswith(b"<!doctype") or b"<table" in head


def _elegir_tabla(tablas):
    """Tabla con columnas de nombre/correo/documento o, si no hay, la de más filas."""
    for t in tablas:
        cols = " ".join(str(c).lower() for c in t.columns)
        if "nombre" in cols or "correo" in cols or "documento" in cols:
            return t
    return max(tablas, key=lambda t: len(t))


def _sin_nan(valor):
    return None if (isinstance(valor, float) and str(valor) == "nan") else valor


def parsear_html_xls(contenido: bytes) -> list[dict[str, str]]:
    """Muchos reportes SENA se exportan como HTML con extensión .xls."""
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("pandas no está instalado para leer HTML/.xls") from e

    texto = contenido.decode("utf-8", errors="replace")
    # Metadato de ficha en el HTML
    ficha_meta = _extraer_numero_ficha_metadato(texto)

    tablas = pd.read_html(io.StringIO(texto))
    if not tablas:
        raise ValueError("No se encontraron tablas en el archivo HTML/.xls.")
    mejor = _elegir_tabla(tablas)

    # A veces la primera fila de datos es la cabecera real
    rows: list[list[Any]] = [list(mejor.columns)]
    rows += [[_sin_nan(v) for v in series.tolist()] for _, series in mejor.iterrows()]
    return _filas_desde_matriz(rows, ficha_meta=ficha_meta)


def _convertir_xls_a_xlsx(contenido: bytes) -> bytes:
    """Convierte .xls antiguo a .xlsx con LibreOffice (si está disponible)."""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "entrada.xls")
        with open(src, "wb") as f:
            f.write(contenido)
        # soffice --headless --convert-to xlsx
        cmd = [
            "soffice",
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--convert-to",
            "xlsx",
            "--outdir",
            tmp,
            src,
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=60,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "No se pudo leer el .xls. Guarda el archivo como .xlsx desde Excel "
                "o instala LibreOffice en el servidor."
            )
        except subprocess.CalledProcessError as e:
            err = (e.stderr or b"").decode("utf-8", errors="replace")[:300]
            raise RuntimeError(
                f"No se pudo convertir el .xls a .xlsx. "
                f"Guarda el archivo como .xlsx e inténtalo de nuevo. Detalle: {err}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                "Tiempo agotado al convertir el .xls. Guarda el archivo como .xlsx."
            ) from e

        out = os.path.join(tmp, "entrada.xlsx")
        if not os.path.isfile(out):
            # A veces el nombre de salida varía
            candidatos = [p for p in os.listdir(tmp) if p.endswith(".xlsx")]
            if not candidatos:
                raise RuntimeError(
                    "La conversión a .xlsx no generó archivo. "
                    "Abre el reporte en Excel y guárdalo como .xlsx."
                )
            out = os.path.join(tmp, candidatos[0])
        with open(out, "rb") as f:
            return f.read()


EXTENSIONES_EXCEL = (".xlsx", ".xls", ".xlsb")


def _leer_con_respaldo_html(contenido: bytes, lector, mensaje=None):
    """Ejecuta `lector`; si falla y el archivo es HTML, lo lee como HTML.
    Si no, lanza RuntimeError(mensaje(e)) o el error original si no hay mensaje."""
    try:
        return lector()
    except Exception as e:
        if _es_html(contenido):
            return parsear_html_xls(contenido)
        if mensaje is None:
            raise
        raise RuntimeError(mensaje(e)) from e


def _mensaje_xlsx(e: Exception) -> str:
    return f"No se pudo leer el Excel (.xlsx): {type(e).__name__}: {e}"


def _mensaje_xls(e: Exception) -> str:
    return (
        "No se pudo leer el archivo .xls. "
        "Ábrelo en Excel y guárdalo como «Libro de Excel (.xlsx)» e inténtalo de nuevo. "
        f"Detalle: {type(e).__name__}: {e}"
    )


def parsear_excel(contenido: bytes, filename: str = "") -> list[dict[str, str]]:
    """
    Lee .xlsx (openpyxl), .xls HTML (pandas) o .xls binario (LibreOffice → xlsx).
    """
    nombre = (filename or "").lower()

    # 1) HTML disfrazado de .xls (muy común en reportes SENA)
    if _es_html(contenido):
        return parsear_html_xls(contenido)

    # 2) .xlsx real
    if nombre.endswith(".xlsx") or contenido[:2] == b"PK":
        return _leer_con_respaldo_html(
            contenido, lambda: parsear_xlsx_bytes(contenido), _mensaje_xlsx
        )

    # 3) .xls antiguo (BIFF) → convertir con LibreOffice
    if nombre.endswith((".xls", ".xlsb")):
        return _leer_con_respaldo_html(
            contenido, lambda: parsear_xlsx_bytes(_convertir_xls_a_xlsx(contenido)), _mensaje_xls
        )

    # 4) Intento genérico openpyxl
    return _leer_con_respaldo_html(contenido, lambda: parsear_xlsx_bytes(contenido))


def parsear_archivo(contenido: bytes, filename: str) -> list[dict[str, str]]:
    if (filename or "").lower().endswith(EXTENSIONES_EXCEL):
        return parsear_excel(contenido, filename)
    return parsear_csv(contenido)


MSG_FALTAN_CAMPOS = "Faltan campos obligatorios (Nombre, Apellidos, Correo Electrónico)."
MSG_SIN_FICHA = (
    "No se encontró número de ficha. "
    "El Excel debe traer «Ficha de Caracterización: NNNNNN» "
    "o la columna numero_ficha."
)


def _limpio(fila: dict[str, str], *claves: str) -> str:
    """Primer valor no vacío de las claves indicadas, sin espacios."""
    return next((fila.get(k) for k in claves if fila.get(k)), "").strip()


def _datos_fila(fila: dict[str, str]) -> dict[str, str]:
    return {
        "nombre": _limpio(fila, "nombre"),
        "apellido": _limpio(fila, "apellido"),
        "correo": _limpio(fila, "correo").lower(),
        "numero_ficha": _limpio(fila, "numero_ficha", "id_ficha"),
        "id_periodo": _limpio(fila, "id_periodo"),
    }


def _buscar_ficha(session: Session, fichas: dict, numero_ficha: str):
    """Ficha por número; si no existe, intenta por id."""
    ficha = fichas.get(numero_ficha)
    if ficha:
        return ficha
    try:
        return session.get(Ficha, int(numero_ficha))
    except ValueError:
        return None


class _Carga:
    """Acumula el resultado de procesar cada fila del archivo."""

    def __init__(self, session: Session, fichas: dict, ficha_fija, id_periodo_default):
        self.session = session
        self.fichas = fichas
        self.ficha_fija = ficha_fija
        self.id_periodo_default = id_periodo_default
        self.creados: list[dict[str, Any]] = []
        self.errores: list[dict[str, Any]] = []
        self.omitidos: list[dict[str, Any]] = []

    def _error(self, i: int, correo: str, mensaje: str) -> None:
        self.errores.append({"fila": i, "correo": correo, "error": mensaje})

    def _ficha(self, d: dict[str, str]):
        """(ficha, mensaje_error)"""
        if self.ficha_fija:
            return self.ficha_fija, None
        numero = d["numero_ficha"]
        if not numero:
            return None, MSG_SIN_FICHA
        ficha = _buscar_ficha(self.session, self.fichas, numero)
        if not ficha:
            return None, f"Ficha '{numero}' no existe. Créala antes de cargar aprendices."
        return ficha, None

    def _periodo(self, d: dict[str, str]):
        """(id_periodo, mensaje_error)"""
        if not d["id_periodo"]:
            return self.id_periodo_default, None
        try:
            return int(d["id_periodo"]), None
        except ValueError:
            return None, f"id_periodo inválido: {d['id_periodo']}"

    def procesar(self, i: int, fila: dict[str, str], enviar_correo: bool) -> None:
        d = _datos_fila(fila)
        campos = (d["nombre"], d["apellido"], d["correo"])
        if not any(campos):
            return
        if not all(campos):
            self._error(i, d["correo"] or "(sin correo)", MSG_FALTAN_CAMPOS)
            return
        ficha, error = self._ficha(d)
        if error is None:
            id_periodo, error = self._periodo(d)
        if error is not None:
            self._error(i, d["correo"], error)
            return
        self._crear(i, d, ficha, id_periodo, enviar_correo)

    def _crear(self, i: int, d: dict, ficha, id_periodo, enviar_correo: bool) -> None:
        correo = d["correo"]
        try:
            data = AprendizCreate(
                nombre=d["nombre"],
                apellido=d["apellido"],
                correo=correo,
                id_ficha=ficha.id_ficha,
                id_periodo=id_periodo,
                enviar_correo=enviar_correo,
            )
            aprendiz = AprendizService.crear(self.session, data)
            self.creados.append({
                "fila": i,
                "correo": correo,
                "id_aprendiz": aprendiz.id_aprendiz,
                "numero_ficha": ficha.numero_ficha,
            })
        except ValueError as e:
            msg = str(e)
            if "Ya existe" in msg:
                self.omitidos.append({"fila": i, "correo": correo, "motivo": msg})
            else:
                self._error(i, correo, msg)
        except Exception as e:
            self._error(i, correo, f"{type(e).__name__}: {e}")


def cargar_desde_filas(
    session: Session,
    filas: list[dict[str, str]],
    id_periodo_default: int | None = None,
    enviar_correo: bool = True,
    id_ficha_forzada: int | None = None,
) -> dict[str, Any]:
    """
    Procesa filas ya parseadas.
    Si id_ficha_forzada se indica, todos los aprendices van a esa ficha
    (útil al subir el reporte dentro del detalle de una ficha).
    """
    fichas = {f.numero_ficha: f for f in session.exec(select(Ficha)).all()}
    ficha_fija = session.get(Ficha, id_ficha_forzada) if id_ficha_forzada else None
    carga = _Carga(session, fichas, ficha_fija, id_periodo_default)
    for i, fila in enumerate(filas, start=2):
        carga.procesar(i, fila, enviar_correo)

    correos = "Se enviaron correos con usuario y contraseña." if enviar_correo \
        else "No se enviaron correos."
    return {
        "total_filas": len(filas),
        "creados": len(carga.creados),
        "omitidos": len(carga.omitidos),
        "errores": len(carga.errores),
        "detalle_creados": carga.creados,
        "detalle_omitidos": carga.omitidos,
        "detalle_errores": carga.errores,
        "mensaje": (
            f"Proceso terminado: {len(carga.creados)} creados, "
            f"{len(carga.omitidos)} omitidos (ya existían), "
            f"{len(carga.errores)} con error. {correos}"
        ),
    }
