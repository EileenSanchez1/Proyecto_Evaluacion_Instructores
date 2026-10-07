"""
Carga masiva de instructores desde CSV (sin foto).

Formato esperado (cabecera flexible, separador ; o ,):

  nombre,apellido,correo,telefono
  Juan,Pérez,juan.perez@sena.edu.co,3001234567

La foto la sube el instructor al entrar (perfil / primer acceso).
Cada fila crea instructor + usuario en modo primer acceso (sin contraseña definitiva).
"""

from __future__ import annotations

import csv
import io
from typing import Any

from sqlmodel import Session

from app.schemas.instructor import InstructorCreate
from app.services.instructor_service import InstructorService


def _normalizar_cabecera(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    n = n.replace(" ", "_").replace("-", "_")
    alias = {
        "email": "correo",
        "mail": "correo",
        "e_mail": "correo",
        "nombres": "nombre",
        "apellidos": "apellido",
        "celular": "telefono",
        "tel": "telefono",
        "phone": "telefono",
    }
    return alias.get(n, n)


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


def cargar_desde_filas(session: Session, filas: list[dict[str, str]]) -> dict[str, Any]:
    creados = []
    omitidos = []
    errores = []

    for i, fila in enumerate(filas, start=2):
        nombre = (fila.get("nombre") or "").strip()
        apellido = (fila.get("apellido") or "").strip()
        correo = (fila.get("correo") or "").strip().lower()
        telefono = (fila.get("telefono") or "").strip() or "0000000000"

        if not nombre or not apellido or not correo:
            errores.append({
                "fila": i,
                "correo": correo or "(vacío)",
                "error": "Faltan nombre, apellido o correo.",
            })
            continue

        if not correo.endswith("@sena.edu.co"):
            errores.append({
                "fila": i,
                "correo": correo,
                "error": "El correo debe ser institucional (@sena.edu.co).",
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
            creados.append({
                "fila": i,
                "correo": correo,
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
            "Sin foto: cada instructor la sube al iniciar sesión en su perfil."
        ),
    }
