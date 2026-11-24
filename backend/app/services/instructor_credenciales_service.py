"""Contraseñas temporales y envío/reenvío de credenciales por correo a instructores."""
import secrets
import string
from typing import Optional

from sqlmodel import Session, select

from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.services.email_service import enviar_credenciales_instructor
from app.services.login_service import LoginService


def generar_password_temporal(longitud: int = 10) -> str:
    """Contraseña temporal legible (letras + dígitos + un símbolo)."""
    simbolos = "!@#$%&*"
    alfabeto = string.ascii_letters + string.digits
    partes = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(simbolos),
    ]
    partes += [secrets.choice(alfabeto) for _ in range(max(0, longitud - 4))]
    secrets.SystemRandom().shuffle(partes)
    return "".join(partes)


def _enviar_correo_credenciales(inst, password_plana: str) -> bool:
    return enviar_credenciales_instructor(
        destinatario=inst.correo,
        nombre=f"{inst.nombre} {inst.apellido}",
        usuario=inst.correo,
        contrasena=password_plana,
    )


def _marcar_credenciales_enviadas(session: Session, usuario) -> None:
    usuario.credenciales_enviadas = True
    session.add(usuario)
    session.commit()


def enviar_credenciales_nuevo(session: Session, usuario, inst, password_plana: str) -> None:
    """Correo de bienvenida al crear el instructor; un fallo no impide la creación."""
    try:
        if _enviar_correo_credenciales(inst, password_plana):
            _marcar_credenciales_enviadas(session, usuario)
    except Exception as e:
        print(f"[EMAIL] No se pudo enviar credenciales a {inst.correo}: {e}")


def _reenviar_a(session: Session, inst, usuario, password_plana: str) -> bool:
    try:
        ok = _enviar_correo_credenciales(inst, password_plana)
    except Exception as e:
        ok = False
        print(f"[EMAIL] instructor {inst.correo}: {e}")
    if ok and usuario:
        _marcar_credenciales_enviadas(session, usuario)
    return bool(ok)


def _instructores_a_notificar(session: Session, id_instructor) -> list:
    if id_instructor is None:
        return list(session.exec(select(Instructor)).all())
    inst = session.get(Instructor, int(id_instructor))
    if inst is None:
        raise ValueError("Instructor no encontrado.")
    return [inst]


def _usuario_y_estado(session: Session, inst) -> tuple:
    """(usuario, activo, ya_recibio_credenciales)"""
    usuario = session.get(Usuario, inst.id_usuario) if inst.id_usuario else None
    if usuario is None:
        return None, True, False
    return usuario, bool(usuario.activo), bool(getattr(usuario, "credenciales_enviadas", False))


def _motivo_omision(activo: bool, ya: bool, solo_activos: bool, solo_pendientes: bool) -> str:
    if solo_activos and not activo:
        return "Inactivo"
    if solo_pendientes and ya:
        return "Ya recibió credenciales"
    return ""


def _nueva_contrasena(session: Session, inst, usuario) -> str:
    """Genera y guarda una contraseña temporal. Devuelve la contraseña en texto plano."""
    password_plana = generar_password_temporal()
    pwd = LoginService.hash_password(password_plana)
    if usuario:
        usuario.contrasena = pwd
        if inst.correo and usuario.correo != inst.correo:
            usuario.correo = inst.correo
        session.add(usuario)
    session.commit()
    return password_plana


def reenviar_credenciales_instructores(
    session: Session,
    solo_activos: bool = True,
    solo_pendientes: bool = True,
    id_instructor: Optional[int] = None,
) -> dict:
    """
    Envía (o reenvía) credenciales a instructores.
    - solo_activos: omite usuarios inactivos
    - solo_pendientes: solo quienes no tienen credenciales_enviadas
    - id_instructor: si se indica, solo ese (siempre envía, aunque ya tenga flag)
    """
    items = _instructores_a_notificar(session, id_instructor)
    # Si se pide un instructor puntual, se envía aunque ya tenga credenciales
    solo_pendientes = solo_pendientes and id_instructor is None

    enviados, omitidos, errores = [], [], []
    for inst in items:
        usuario, activo, ya = _usuario_y_estado(session, inst)
        motivo = _motivo_omision(activo, ya, solo_activos, solo_pendientes)
        if motivo:
            omitidos.append({"correo": inst.correo, "motivo": motivo})
            continue
        password_plana = _nueva_contrasena(session, inst, usuario)
        if _reenviar_a(session, inst, usuario, password_plana):
            enviados.append(inst.correo)
        else:
            errores.append({"correo": inst.correo, "error": "SMTP falló"})

    return {
        "enviados": len(enviados),
        "omitidos": len(omitidos),
        "errores": len(errores),
        "detalle_enviados": enviados,
        "detalle_omitidos": omitidos,
        "detalle_errores": errores,
        "mensaje": (
            f"Correos enviados: {len(enviados)}. "
            f"Omitidos: {len(omitidos)}. Fallidos: {len(errores)}."
        ),
    }
