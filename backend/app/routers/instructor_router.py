import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlmodel import Session
from typing import List, Optional

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.instructor import InstructorCreate, InstructorRead, InstructorUpdate
from app.services.instructor_service import InstructorService


router = APIRouter(
    prefix="/instructores",
    tags=["Instructores"]
)

# CORREGIDO: misma carpeta que main.py sirve como /uploads
# (sube 2 niveles desde routers/ -> app/, luego entra a uploads/)
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def _guardar_foto(foto: UploadFile, instructor_id: int) -> str:
    if not foto or not foto.filename:
        return None

    ext = os.path.splitext(foto.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise ValueError("Formato de imagen no válido. Use JPG, PNG, GIF o WEBP.")

    # Eliminar fotos anteriores del mismo instructor (cualquier extensión)
    for old_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        old_ruta = os.path.join(UPLOADS_DIR, f"instructor_{instructor_id}{old_ext}")
        if os.path.exists(old_ruta):
            os.remove(old_ruta)

    nombre_archivo = f"instructor_{instructor_id}{ext}"
    ruta_archivo = os.path.join(UPLOADS_DIR, nombre_archivo)

    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    return f"/uploads/{nombre_archivo}"


@router.post(
    "/",
    response_model=InstructorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def crear_instructor(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    competencias: str = Form("[]"),
    foto: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    try:
        import json
        ids_competencias = json.loads(competencias)
        if not isinstance(ids_competencias, list):
            ids_competencias = []

        instructor_data = InstructorCreate(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            foto=None,
            competencias=ids_competencias
        )

        resultado = InstructorService.crear(session, instructor_data)

        if foto:
            foto_url = _guardar_foto(foto, resultado["id_instructor"])
            from app.schemas.instructor import InstructorUpdate
            InstructorService.actualizar(
                session,
                resultado["id_instructor"],
                InstructorUpdate(foto=foto_url)
            )
            resultado["foto"] = foto_url

        return resultado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al crear instructor: {str(e)}")


@router.get("/", response_model=List[InstructorRead])
def listar_instructores(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    try:
        return InstructorService.listar(session, offset, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar instructores: {str(e)}")


@router.get("/{instructor_id}", response_model=InstructorRead)
def buscar_instructor(
    instructor_id: int,
    session: Session = Depends(get_session)
):
    instructor = InstructorService.buscar(session, instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return instructor


@router.put(
    "/{instructor_id}",
    response_model=InstructorRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def actualizar_instructor(
    instructor_id: int,
    nombre: Optional[str] = Form(None),
    apellido: Optional[str] = Form(None),
    correo: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    competencias: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    try:
        import json

        update_data = {}
        if nombre is not None:
            update_data["nombre"] = nombre
        if apellido is not None:
            update_data["apellido"] = apellido
        if correo is not None:
            update_data["correo"] = correo
        if telefono is not None:
            update_data["telefono"] = telefono
        if competencias is not None:
            update_data["competencias"] = json.loads(competencias)

        if foto and foto.filename:
            foto_url = _guardar_foto(foto, instructor_id)
            update_data["foto"] = foto_url

        instructor_update = InstructorUpdate(**update_data)

        instructor = InstructorService.actualizar(
            session,
            instructor_id,
            instructor_update
        )

        if not instructor:
            raise HTTPException(status_code=404, detail="Instructor no encontrado")

        return instructor
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{instructor_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))]
)
def eliminar_instructor(
    instructor_id: int,
    session: Session = Depends(get_session)
):
    # Eliminar archivo de foto si existe
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        ruta = os.path.join(UPLOADS_DIR, f"instructor_{instructor_id}{ext}")
        if os.path.exists(ruta):
            os.remove(ruta)

    eliminado = InstructorService.eliminar(session, instructor_id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")

    return {"mensaje": "Instructor eliminado correctamente"}
