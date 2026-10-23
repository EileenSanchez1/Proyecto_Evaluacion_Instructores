"""
Gestión de administradores del sistema.

Solo el rol Administrador puede:
- Listar administradores
- Invitar / promover a Administrador por correo
- Desactivar un administrador
- Degradar a Coordinador

Regla de seguridad: siempre debe quedar al menos un Administrador activo.
"""

from __future__ import annotations

import secrets
import string
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.config.auth_dependencies import get_current_user, require_roles
from app.config.database import get_session
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.services.login_service import LoginService

router = APIRouter(prefix="/admin-usuarios", tags=["Admin usuarios"])

ROLES_ADMIN = ("Administrador", "Admin")


def _rol_por_nombre(session: Session, nombre: str) -> Rol:
    rol = session.exec(select(Rol).where(Rol.nombre == nombre)).first()
    if not rol:
        raise HTTPException(
            status_code=500,
            detail=f"El rol '{nombre}' no existe. Ejecuta seed_roles.py.",
        )
    return rol


def _es_admin(usuario: Usuario) -> bool:
    return bool(usuario.rol and usuario.rol.nombre in ROLES_ADMIN)


def _contar_admins_activos(session: Session, excluir_id: Optional[int] = None) -> int:
    rol_admin = session.exec(select(Rol).where(Rol.nombre == "Administrador")).first()
    if not rol_admin:
        return 0
    stmt = select(Usuario).where(
        Usuario.id_rol == rol_admin.id_rol,
        Usuario.activo == True,  # noqa: E712
    )
    usuarios = session.exec(stmt).all()
    if excluir_id is not None:
        usuarios = [u for u in usuarios if u.id_usuario != excluir_id]
    return len(usuarios)


def _usuario_a_dict(u: Usuario) -> dict:
    return {
        "id_usuario": u.id_usuario,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "correo": u.correo,
        "rol": u.rol.nombre if u.rol else None,
        "activo": u.activo,
        "fecha_creacion": u.fecha_creacion.isoformat() if u.fecha_creacion else None,
    }


def _generar_password_temporal(longitud: int = 12) -> str:
    """Contraseña temporal que cumple la política de seguridad del sistema."""
    mayus = secrets.choice(string.ascii_uppercase)
    minus = secrets.choice(string.ascii_lowercase)
    digito = secrets.choice(string.digits)
    especial = secrets.choice("!@#$%&*")
    resto = "".join(
        secrets.choice(string.ascii_letters + string.digits + "!@#$%&*")
        for _ in range(max(0, longitud - 4))
    )
    chars = list(mayus + minus + digito + especial + resto)
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


class PromoverAdminRequest(BaseModel):
    correo: EmailStr
    nombre: Optional[str] = Field(default=None, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)


@router.get(
    "/administradores",
    dependencies=[Depends(require_roles("Administrador"))],
)
def listar_administradores(session: Session = Depends(get_session)):
    """Lista todos los usuarios con rol Administrador (activos e inactivos)."""
    rol_admin = _rol_por_nombre(session, "Administrador")
    usuarios = list(
        session.exec(select(Usuario).where(Usuario.id_rol == rol_admin.id_rol)).all()
    )
    usuarios.sort(key=lambda u: ((u.nombre or "").lower(), (u.apellido or "").lower()))
    return {
        "total": len(usuarios),
        "activos": sum(1 for u in usuarios if u.activo),
        "administradores": [_usuario_a_dict(u) for u in usuarios],
    }


@router.post(
    "/promover",
    dependencies=[Depends(require_roles("Administrador"))],
)
def promover_administrador(
    datos: PromoverAdminRequest,
    session: Session = Depends(get_session),
    actual: Usuario = Depends(get_current_user),
):
    """
    Invita o promueve a un usuario como Administrador.

    - Si el correo ya existe: cambia su rol a Administrador y lo reactiva.
    - Si no existe: crea el usuario con una contraseña temporal (se devuelve una sola vez).
    """
    correo = str(datos.correo).strip().lower()
    if not correo:
        raise HTTPException(status_code=400, detail="Correo requerido.")

    rol_admin = _rol_por_nombre(session, "Administrador")
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()

    password_temporal = None
    creado = False

    if usuario:
        if _es_admin(usuario) and usuario.activo:
            return {
                "mensaje": "Este usuario ya es administrador activo.",
                "creado": False,
                "promovido": False,
                "usuario": _usuario_a_dict(usuario),
                "password_temporal": None,
            }
        usuario.id_rol = rol_admin.id_rol
        usuario.activo = True
        if datos.nombre and datos.nombre.strip():
            usuario.nombre = datos.nombre.strip()
        if datos.apellido and datos.apellido.strip():
            usuario.apellido = datos.apellido.strip()
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return {
            "mensaje": (
                f"Usuario {correo} promovido a Administrador. "
                "Puede iniciar sesión con su contraseña actual en la pestaña Soy Admin."
            ),
            "creado": False,
            "promovido": True,
            "usuario": _usuario_a_dict(usuario),
            "password_temporal": None,
        }

    # Crear nuevo administrador
    nombre = (datos.nombre or "").strip() or "Administrador"
    apellido = (datos.apellido or "").strip() or "Sistema"
    password_temporal = _generar_password_temporal()
    usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        contrasena=LoginService.hash_password(password_temporal),
        id_rol=rol_admin.id_rol,
        activo=True,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    creado = True

    # Intentar notificar por correo (no bloquea si falla)
    try:
        from app.services.email_service import enviar_correo

        enviar_correo(
            correo,
            "Acceso de Administrador — Evaluación de Instructores SENA",
            (
                f"Hola {nombre},\n\n"
                "Se te asignó el rol de Administrador en el sistema de Evaluación de Instructores.\n\n"
                f"Correo: {correo}\n"
                f"Contraseña temporal: {password_temporal}\n\n"
                "Ingresa en la pestaña «Soy Admin», usa esta contraseña y el código que recibirás por correo.\n"
                "Te recomendamos cambiar la contraseña después del primer acceso.\n\n"
                "— Sistema SENA Evaluación de Instructores\n"
            ),
        )
    except Exception as e:
        print(f"[ADMIN] No se pudo enviar correo de invitación: {e}")

    print(f"\n{'='*50}")
    print(f"[ADMIN] Nuevo admin creado: {correo}")
    print(f"[ADMIN] Contraseña temporal: {password_temporal}")
    print(f"{'='*50}\n")

    return {
        "mensaje": (
            f"Administrador creado: {correo}. "
            "Guarda la contraseña temporal; solo se muestra una vez. "
            "También se intentó enviar por correo."
        ),
        "creado": creado,
        "promovido": False,
        "usuario": _usuario_a_dict(usuario),
        "password_temporal": password_temporal,
    }


@router.post(
    "/{id_usuario}/desactivar",
    dependencies=[Depends(require_roles("Administrador"))],
)
def desactivar_administrador(
    id_usuario: int,
    session: Session = Depends(get_session),
    actual: Usuario = Depends(get_current_user),
):
    """Desactiva un administrador. No permite dejar el sistema sin ningún admin activo."""
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not _es_admin(usuario):
        raise HTTPException(status_code=400, detail="El usuario no es administrador.")
    if not usuario.activo:
        return {"mensaje": "El administrador ya estaba inactivo.", "usuario": _usuario_a_dict(usuario)}

    if _contar_admins_activos(session, excluir_id=id_usuario) < 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "No se puede desactivar: debe quedar al menos un administrador activo. "
                "Primero promueve a otra persona y luego desactiva esta cuenta."
            ),
        )

    usuario.activo = False
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {
        "mensaje": f"Administrador {usuario.correo} desactivado.",
        "usuario": _usuario_a_dict(usuario),
    }


@router.post(
    "/{id_usuario}/reactivar",
    dependencies=[Depends(require_roles("Administrador"))],
)
def reactivar_administrador(
    id_usuario: int,
    session: Session = Depends(get_session),
):
    """Reactiva un administrador previamente desactivado."""
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not _es_admin(usuario):
        raise HTTPException(status_code=400, detail="El usuario no es administrador.")
    usuario.activo = True
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {
        "mensaje": f"Administrador {usuario.correo} reactivado.",
        "usuario": _usuario_a_dict(usuario),
    }


@router.post(
    "/{id_usuario}/degradar-coordinador",
    dependencies=[Depends(require_roles("Administrador"))],
)
def degradar_a_coordinador(
    id_usuario: int,
    session: Session = Depends(get_session),
    actual: Usuario = Depends(get_current_user),
):
    """
    Quita el rol Administrador y deja al usuario como Coordinador.
    Útil cuando el coordinador anterior sigue en el centro pero ya no debe ser admin.
    """
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not _es_admin(usuario):
        raise HTTPException(status_code=400, detail="El usuario no es administrador.")

    if usuario.activo and _contar_admins_activos(session, excluir_id=id_usuario) < 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "No se puede degradar: debe quedar al menos un administrador activo. "
                "Promueve primero a la persona que asumirá el rol."
            ),
        )

    rol_coord = _rol_por_nombre(session, "Coordinador")
    usuario.id_rol = rol_coord.id_rol
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {
        "mensaje": f"{usuario.correo} ahora es Coordinador (ya no es Administrador).",
        "usuario": _usuario_a_dict(usuario),
    }
