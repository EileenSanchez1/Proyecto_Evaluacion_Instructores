from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from typing import List, Optional
import os
import shutil
import json
import uuid
import time

from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.schemas.instructor import InstructorCreate, InstructorRead, InstructorUpdate
from app.services.instructor_service import InstructorService
from app.models.usuario import Usuario

router = APIRouter(prefix="/instructores", tags=["Instructores"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/",
    response_model=InstructorRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
async def crear_instructor(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    competencias: str = Form("[]"),
    foto: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    correo = correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(
            status_code=400,
            detail="El correo del instructor debe ser institucional (@sena.edu.co).",
        )

    try:
        lista_comp = json.loads(competencias) if competencias else []
        if not isinstance(lista_comp, list):
            lista_comp = []
        lista_comp = [int(x) for x in lista_comp]
    except (json.JSONDecodeError, TypeError, ValueError):
        lista_comp = []

    foto_url = None
    if foto and foto.filename:
        ext = os.path.splitext(foto.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten imágenes JPG, PNG, GIF o WEBP.",
            )
        filename = f"instructor_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/uploads/{filename}"

    datos = InstructorCreate(
        nombre=nombre.strip(),
        apellido=apellido.strip(),
        correo=correo,
        telefono=telefono.strip(),
        foto=foto_url,
        competencias=lista_comp,
    )

    try:
        inst = InstructorService.crear(session, datos)
        return InstructorService.to_read(session, inst)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[InstructorRead])
def listar_instructores(
    incluir_inactivos: bool = False,
    session: Session = Depends(get_session),
):
    """Por defecto solo activos. Admin puede pasar incluir_inactivos=true."""
    items = InstructorService.listar(session, incluir_inactivos=incluir_inactivos)
    return [InstructorService.to_read(session, i) for i in items]


@router.get("/{instructor_id}", response_model=InstructorRead)
def buscar_instructor(instructor_id: int, session: Session = Depends(get_session)):
    inst = InstructorService.buscar(session, instructor_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return InstructorService.to_read(session, inst)


@router.put(
    "/{instructor_id}",
    response_model=InstructorRead,
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def actualizar_instructor(
    instructor_id: int,
    datos: InstructorUpdate,
    session: Session = Depends(get_session),
):
    """Actualiza datos del instructor (JSON). La foto se sube en POST /{id}/foto."""
    try:
        inst = InstructorService.actualizar(session, instructor_id, datos)
        if not inst:
            raise HTTPException(status_code=404, detail="Instructor no encontrado")
        return InstructorService.to_read(session, inst)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{instructor_id}/reset-primer-acceso",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def reset_primer_acceso(instructor_id: int, session: Session = Depends(get_session)):
    """
    Pone al instructor en modo primer acceso:
    al entrar con su correo pedirá código + crear contraseña.
    Útil para instructores creados/migrados antes del flujo actual.
    """
    ok = InstructorService.resetear_primer_acceso(session, instructor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return {
        "mensaje": "Instructor en modo primer acceso. Debe ingresar con código y crear contraseña."
    }


@router.delete(
    "/{instructor_id}",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def eliminar_instructor(instructor_id: int, session: Session = Depends(get_session)):
    """Desactiva (no borra) al instructor. Puede reactivarse después."""
    try:
        ok = InstructorService.eliminar(session, instructor_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return {"mensaje": "Instructor desactivado correctamente. Puedes reactivarlo cuando regrese."}


@router.post(
    "/{instructor_id}/reactivar",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def reactivar_instructor(instructor_id: int, session: Session = Depends(get_session)):
    try:
        ok = InstructorService.reactivar(session, instructor_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return {"mensaje": "Instructor reactivado correctamente."}


@router.post("/{instructor_id}/foto", response_model=InstructorRead)
def subir_foto_instructor(
    instructor_id: int,
    foto: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    instructor = InstructorService.buscar(session, instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")

    ext = os.path.splitext(foto.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=400, detail="Solo se permiten imágenes JPG, PNG o WEBP."
        )

    filename = f"instructor_{instructor_id}_{int(time.time())}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    foto_url = f"/uploads/{filename}"
    actualizado = InstructorService.actualizar_foto(session, instructor_id, foto_url)
    return actualizado
