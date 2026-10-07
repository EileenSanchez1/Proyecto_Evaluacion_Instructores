"""
Carga masiva de aprendices desde archivo plano (CSV).

Formato esperado (cabecera flexible, separador ; o ,):

  nombre,apellido,correo,numero_ficha
  Ana,Pérez,ana.perez@correo.com,2874194

Opcional: id_periodo (si no, usa el periodo activo).

Cada fila:
  - Crea aprendiz + usuario ya asignado a la ficha
  - Genera contraseña temporal
  - Envía correo con usuario/contraseña (cartero)
"""

from __future__ import annotations

import csv
import io
from typing import Any

from sqlmodel import Session, select

from app.models.ficha import Ficha
from app.schemas.aprendiz import AprendizCreate
from app.services.aprendiz_service import AprendizService


def _normalizar_cabecera(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    n = n.replace(" ", "_").replace("-", "_")
    alias = {
        "email": "correo",
        "mail": "correo",
        "e_mail": "correo",
        "ficha": "numero_ficha",
        "n_ficha": "numero_ficha",
        "num_ficha": "numero_ficha",
        "numero": "numero_ficha",
        "nombres": "nombre",
        "apellidos": "apellido",
        "periodo": "id_periodo",
        "idperiodo": "id_periodo",
    }
    return alias.get(n, n)


def parsear_csv(contenido: bytes | str) -> list[dict[str, str]]:
    if isinstance(contenido, bytes):
        # Quitar BOM UTF-8 si existe
        if contenido.startswith(b"\xef\xbb\xbf"):
            contenido = contenido[3:]
        texto = contenido.decode("utf-8", errors="replace")
    else:
        texto = contenido

    # Detectar separador
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


def cargar_desde_filas(
    session: Session,
    filas: list[dict[str, str]],
    id_periodo_default: int | None = None,
    enviar_correo: bool = True,
) -> dict[str, Any]:
    """
    Procesa filas ya parseadas.
    Retorna resumen: creados, errores, omitidos.
    """
    # Cache fichas por número
    fichas = {f.numero_ficha: f for f in session.exec(select(Ficha)).all()}

    creados = []
    errores = []
    omitidos = []

    for i, fila in enumerate(filas, start=2):  # fila 1 = cabecera
        nombre = fila.get("nombre", "").strip()
        apellido = fila.get("apellido", "").strip()
        correo = fila.get("correo", "").strip().lower()
        numero_ficha = (
            fila.get("numero_ficha")
            or fila.get("id_ficha")
            or ""
        ).strip()
        id_periodo_raw = fila.get("id_periodo", "").strip()

        if not nombre and not apellido and not correo:
            continue  # fila vacía

        if not nombre or not apellido or not correo or not numero_ficha:
            errores.append({
                "fila": i,
                "correo": correo or "(sin correo)",
                "error": "Faltan campos obligatorios (nombre, apellido, correo, numero_ficha).",
            })
            continue

        ficha = fichas.get(numero_ficha)
        if not ficha:
            # Intentar como id numérico
            try:
                id_f = int(numero_ficha)
                ficha = session.get(Ficha, id_f)
            except ValueError:
                ficha = None
        if not ficha:
            errores.append({
                "fila": i,
                "correo": correo,
                "error": f"Ficha '{numero_ficha}' no existe. Créala antes de cargar aprendices.",
            })
            continue

        id_periodo = id_periodo_default
        if id_periodo_raw:
            try:
                id_periodo = int(id_periodo_raw)
            except ValueError:
                errores.append({
                    "fila": i,
                    "correo": correo,
                    "error": f"id_periodo inválido: {id_periodo_raw}",
                })
                continue

        try:
            data = AprendizCreate(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                id_ficha=ficha.id_ficha,
                id_periodo=id_periodo,
                enviar_correo=enviar_correo,
            )
            aprendiz = AprendizService.crear(session, data)
            creados.append({
                "fila": i,
                "correo": correo,
                "id_aprendiz": aprendiz.id_aprendiz,
                "numero_ficha": ficha.numero_ficha,
            })
        except ValueError as e:
            msg = str(e)
            if "Ya existe" in msg:
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
            f"{'Se enviaron correos con usuario y contraseña.' if enviar_correo else 'No se enviaron correos.'}"
        ),
    }
