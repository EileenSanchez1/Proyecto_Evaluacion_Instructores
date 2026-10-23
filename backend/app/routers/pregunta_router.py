from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.pregunta import (
    PreguntaCreate,
    PreguntaRead,
    PreguntaUpdate
)
from app.services.pregunta_service import PreguntaService

router = APIRouter(
    prefix="/preguntas",
    tags=["Preguntas"]
)


@router.post("/", response_model=PreguntaRead)
def crear_pregunta(
    pregunta: PreguntaCreate,
    session: Session = Depends(get_session)
):
    return PreguntaService.crear(
        session,
        pregunta
    )


@router.get("/", response_model=List[PreguntaRead])
def listar_preguntas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return PreguntaService.listar(
        session,
        offset,
        limit
    )


@router.get("/activas", response_model=List[PreguntaRead])
def listar_preguntas_activas(
    session: Session = Depends(get_session)
):
    return PreguntaService.listar_activas(session)


@router.get("/{pregunta_id}", response_model=PreguntaRead)
def buscar_pregunta(
    pregunta_id: int,
    session: Session = Depends(get_session)
):
    pregunta = PreguntaService.buscar(
        session,
        pregunta_id
    )

    if not pregunta:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return pregunta


@router.put("/{pregunta_id}", response_model=PreguntaRead)
def actualizar_pregunta(
    pregunta_id: int,
    pregunta_update: PreguntaUpdate,
    session: Session = Depends(get_session)
):
    pregunta = PreguntaService.actualizar(
        session,
        pregunta_id,
        pregunta_update
    )

    if not pregunta:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return pregunta


@router.delete("/{pregunta_id}")
def eliminar_pregunta(
    pregunta_id: int,
    session: Session = Depends(get_session)
):
    eliminado = PreguntaService.eliminar(
        session,
        pregunta_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return {
        "mensaje": "Pregunta eliminada correctamente"
    }

@router.post(
    "/cargar-oficiales",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def cargar_preguntas_oficiales(
    reemplazar: bool = Query(False, description="Si true, desactiva las preguntas actuales y carga las oficiales"),
    session: Session = Depends(get_session),
):
    """
    Carga las 19 preguntas del formato oficial SENA
    (Evaluación de instructores en aula).
    Por defecto solo agrega las que no existen (por descripción).
    Con reemplazar=true desactiva las actuales y crea las oficiales.
    """
    import json
    from pathlib import Path
    from app.models.pregunta import Pregunta
    from sqlmodel import select

    data_path = Path(__file__).resolve().parents[1] / "data" / "preguntas_oficiales_sena.json"
    if not data_path.exists():
        raise HTTPException(status_code=500, detail="Archivo de preguntas oficiales no encontrado.")

    with open(data_path, encoding="utf-8") as f:
        oficiales = json.load(f)

    if reemplazar:
        existentes = session.exec(select(Pregunta)).all()
        for p in existentes:
            p.estado = False
            session.add(p)
        session.commit()

    creadas = 0
    omitidas = 0
    for item in oficiales:
        desc = (item.get("descripcion") or "").strip()
        orden = int(item.get("orden") or 0)
        if not desc:
            continue
        ya = session.exec(
            select(Pregunta).where(Pregunta.descripcion == desc)
        ).first()
        if ya:
            if reemplazar:
                ya.estado = True
                ya.orden = orden
                session.add(ya)
            omitidas += 1
            continue
        p = Pregunta(descripcion=desc, orden=orden, estado=True)
        session.add(p)
        creadas += 1

    session.commit()
    return {
        "mensaje": f"Preguntas oficiales SENA: {creadas} creadas, {omitidas} ya existían.",
        "creadas": creadas,
        "omitidas": omitidas,
        "reemplazar": reemplazar,
        "total_oficiales": len(oficiales),
    }


@router.post(
    "/carga-excel",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
async def cargar_preguntas_excel(
    archivo: UploadFile = File(...),
    reemplazar: bool = Query(
        False,
        description="Si true, desactiva las preguntas actuales y carga solo las del Excel",
    ),
    session: Session = Depends(get_session),
):
    """
    Carga preguntas desde el Excel del formato oficial SENA
    (Evaluación de instructores en aula). Solo se toman las filas de preguntas.
    """
    nombre = (archivo.filename or "").lower()
    es_excel = nombre.endswith(".xlsx") or nombre.endswith(".xls")
    es_csv = nombre.endswith(".csv") or nombre.endswith(".txt") or nombre.endswith(".tsv")
    if not (es_excel or es_csv):
        raise HTTPException(
            status_code=400,
            detail="Sube un archivo Excel (.xlsx) o CSV (.csv) del formato de evaluación de instructores.",
        )
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    from app.services.carga_preguntas_service import (
        parsear_xlsx_preguntas,
        parsear_csv_preguntas,
        cargar_preguntas_desde_filas,
    )

    try:
        if es_csv:
            filas = parsear_csv_preguntas(contenido)
        else:
            filas = parsear_xlsx_preguntas(contenido)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo leer el archivo: {type(e).__name__}: {e}",
        )

    if not filas:
        raise HTTPException(
            status_code=400,
            detail="No se detectaron preguntas en el archivo. Verifica el formato SENA.",
        )

    return cargar_preguntas_desde_filas(session, filas, reemplazar=reemplazar)
