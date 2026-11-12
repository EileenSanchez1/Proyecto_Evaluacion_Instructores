from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.config.database import get_session
from app.config.security import (
    crear_access_token, verificar_codigo, limpiar_codigo,
    crear_token_recuperacion, verificar_token_recuperacion
)
from app.schemas.login import (
    LoginRequest, LoginResponse, SolicitarRecuperacionRequest,
    VerificarCodigoRequest, RestablecerPasswordRequest,
    LoginInstructorRequest, VerificarCodigoInstructorRequest,
    InstructorCorreoRequest, InstructorCrearPasswordRequest,
    CambiarPasswordRequest,
)
from app.services.login_service import LoginService
from app.models.aprendiz import Aprendiz
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.config.auth_dependencies import get_current_user

router = APIRouter(prefix="/login", tags=["Login"])

def _usuario_a_dict(usuario):
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre,
        "foto": usuario.foto
    }

@router.post("/", response_model=LoginResponse)
def login(datos: LoginRequest, session: Session = Depends(get_session)):
    """
    Portal APRENDIZ únicamente.
    Instructor / Admin / Coordinador deben usar su propio acceso.
    """
    # NO validar fortaleza aquí: las contraseñas temporales del cartero
    # (carga masiva) deben poder usarse para el primer ingreso.
    usuario, mensaje = LoginService.validar_login(session, datos.correo, datos.contrasena)
    if usuario is None:
        raise HTTPException(status_code=401, detail=mensaje)

    nombre_rol = (usuario.rol.nombre if usuario.rol else "") or ""
    if nombre_rol != "Aprendiz":
        # Credenciales válidas pero portal incorrecto: no entregar token
        if nombre_rol in ("Instructor",):
            raise HTTPException(
                status_code=403,
                detail="Esta cuenta es de instructor. Usa el acceso «Soy instructor».",
            )
        if nombre_rol in ("Administrador", "Admin", "Coordinador"):
            raise HTTPException(
                status_code=403,
                detail="Esta cuenta es de administración. Usa el acceso de administrador.",
            )
        raise HTTPException(
            status_code=403,
            detail="Esta cuenta no corresponde al acceso de aprendiz.",
        )

    aprendiz = session.exec(
        select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)
    ).first()
    if not aprendiz:
        raise HTTPException(
            status_code=403,
            detail="Tu usuario no está vinculado a un aprendiz. Contacta a coordinación.",
        )

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol="Aprendiz",
    )

    usuario_data = _usuario_a_dict(usuario)
    usuario_data["id_aprendiz"] = aprendiz.id_aprendiz
    usuario_data["id_ficha"] = aprendiz.id_ficha
    usuario_data["id_periodo"] = getattr(aprendiz, "id_periodo", None)

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)

# =========================
# RECUPERACIÓN POR CÓDIGO
# =========================
@router.post("/recuperar", response_model=dict)
def solicitar_recuperacion(datos: SolicitarRecuperacionRequest, session: Session = Depends(get_session)):
    correo = datos.correo.strip().lower()
    usuario = LoginService.buscar_por_correo(session, correo)
    if usuario:
        LoginService.enviar_codigo_recuperacion(usuario.correo.strip().lower())
    return {
        "mensaje": "Si el correo está registrado, recibirás un código de verificación en unos minutos. Revisa tu bandeja de entrada y spam."
    }

@router.post("/verificar-codigo", response_model=dict)
def verificar_codigo_recuperacion(datos: VerificarCodigoRequest):
    # Solo valida; NO consume el código (se consume al restablecer)
    correo = datos.correo.strip().lower()
    if not verificar_codigo(correo, datos.codigo.strip(), tipo="recuperacion", consumir=False):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")
    return {"mensaje": "Código verificado correctamente.", "valido": True}

@router.post("/restablecer", response_model=dict)
def restablecer_password(datos: RestablecerPasswordRequest, session: Session = Depends(get_session)):
    es_segura, msg = LoginService.validar_contrasena_segura(datos.nueva_contrasena)
    if not es_segura:
        raise HTTPException(status_code=400, detail=f"La contraseña no es segura: {msg}")

    correo = datos.correo.strip().lower()
    codigo = datos.codigo.strip()

    if not verificar_codigo(correo, codigo, tipo="recuperacion", consumir=True):
        raise HTTPException(
            status_code=400,
            detail="Código inválido o expirado. Solicita uno nuevo.",
        )

    usuario = LoginService.buscar_por_correo(session, correo)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    _, mensaje = LoginService.restablecer_password(session, usuario, datos.nueva_contrasena)
    limpiar_codigo(correo, tipo="recuperacion")
    return {"mensaje": mensaje}


@router.post("/cambiar-password")
def cambiar_password(
    datos: CambiarPasswordRequest,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    """Cambio de contraseña estando autenticado (aprendiz/instructor/admin)."""
    if not LoginService.verificar_password(datos.contrasena_actual, usuario.contrasena):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta.")
    es_segura, msg = LoginService.validar_contrasena_segura(datos.nueva_contrasena)
    if not es_segura:
        raise HTTPException(status_code=400, detail=msg)
    LoginService.restablecer_password(session, usuario, datos.nueva_contrasena)
    # Sincronizar hash en tabla aprendices si aplica
    aprendiz = session.exec(
        select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)
    ).first()
    if aprendiz:
        aprendiz.contrasena = usuario.contrasena
        session.add(aprendiz)
        session.commit()
    return {"mensaje": "Contraseña actualizada correctamente."}


# =========================
# LOGIN INSTRUCTOR
# =========================
def _exigir_usuario_instructor(session: Session, correo: str):
    """Valida que el correo sea instructor real (tabla + rol)."""
    instructor = LoginService.buscar_instructor_por_correo(session, correo)
    if not instructor:
        raise HTTPException(
            status_code=404,
            detail="No hay un instructor registrado con ese correo. Si eres aprendiz o admin, usa tu acceso correspondiente.",
        )

    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Cuenta de instructor no activa.")

    nombre_rol = (usuario.rol.nombre if usuario.rol else "") or ""
    if nombre_rol != "Instructor":
        raise HTTPException(
            status_code=403,
            detail="Esta cuenta no tiene rol de instructor. Usa el acceso que corresponde a tu rol.",
        )

    # Coherencia: el usuario del instructor debe coincidir
    if instructor.id_usuario and instructor.id_usuario != usuario.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="La cuenta de instructor no está vinculada correctamente. Contacta a coordinación.",
        )

    return instructor, usuario


@router.post("/instructor/iniciar", response_model=dict)
def instructor_iniciar(datos: InstructorCorreoRequest, session: Session = Depends(get_session)):
    """Portal INSTRUCTOR: solo correo; detecta primer acceso o login normal."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="El correo debe ser institucional (@sena.edu.co).")

    _exigir_usuario_instructor(session, correo)

    if LoginService.instructor_necesita_crear_password(session, correo):
        LoginService.enviar_codigo_instructor(correo)
        return {
            "mensaje": "Primer acceso: se envió un código a tu correo institucional. Revisa bandeja de entrada y spam. Luego crea tu contraseña.",
            "requiere_crear_password": True,
            "email_enviado": True,
        }

    return {
        "mensaje": "Ingresa tu contraseña para continuar.",
        "requiere_crear_password": False,
    }


@router.post("/instructor/crear-password", response_model=LoginResponse)
def instructor_crear_password(datos: InstructorCrearPasswordRequest, session: Session = Depends(get_session)):
    """Portal INSTRUCTOR — primer acceso: código + nueva contraseña."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="Correo inválido.")

    instructor, _usuario_prev = _exigir_usuario_instructor(session, correo)

    if not verificar_codigo(correo, datos.codigo, tipo="instructor"):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    if not LoginService.instructor_necesita_crear_password(session, correo):
        raise HTTPException(status_code=400, detail="Esta cuenta ya tiene contraseña.")

    usuario, mensaje = LoginService.establecer_password_instructor(session, correo, datos.nueva_contrasena)
    if not usuario:
        raise HTTPException(status_code=400, detail=mensaje)

    limpiar_codigo(correo, tipo="instructor")

    # Revalidar rol tras establecer password
    nombre_rol = (usuario.rol.nombre if usuario.rol else "") or ""
    if nombre_rol != "Instructor":
        raise HTTPException(status_code=403, detail="Esta cuenta no tiene rol de instructor.")

    token = crear_access_token(id_usuario=usuario.id_usuario, correo=usuario.correo, rol="Instructor")
    usuario_data = _usuario_a_dict(usuario)
    usuario_data["id_instructor"] = instructor.id_instructor
    if instructor.foto:
        usuario_data["foto"] = instructor.foto

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)


@router.post("/instructor", response_model=LoginResponse)
def login_instructor_directo(datos: LoginInstructorRequest, session: Session = Depends(get_session)):
    """Portal INSTRUCTOR — login normal: correo + contraseña."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="El correo debe ser institucional (@sena.edu.co).")

    instructor, usuario = _exigir_usuario_instructor(session, correo)

    if LoginService.instructor_necesita_crear_password(session, correo):
        raise HTTPException(status_code=400, detail="Debes crear tu contraseña primero (primer acceso).")

    if not LoginService.verificar_password(datos.contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    token = crear_access_token(id_usuario=usuario.id_usuario, correo=usuario.correo, rol="Instructor")
    usuario_data = _usuario_a_dict(usuario)
    usuario_data["id_instructor"] = instructor.id_instructor
    if instructor.foto:
        usuario_data["foto"] = instructor.foto

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)


# =========================
# ADMIN: segundo factor por código al Gmail
# =========================
@router.post("/admin/iniciar")
def admin_iniciar(datos: LoginRequest, session: Session = Depends(get_session)):
    """
    Valida correo + contraseña de un Administrador y, si es correcto,
    envía un código de verificación al correo (Gmail) para segundo factor.
    """
    correo = datos.correo.strip().lower()
    usuario, mensaje = LoginService.validar_login(session, correo, datos.contrasena)
    if usuario is None:
        raise HTTPException(status_code=401, detail=mensaje)

    nombre_rol = (usuario.rol.nombre if usuario.rol else "") or ""
    if nombre_rol not in ("Administrador", "Admin"):
        if nombre_rol == "Instructor":
            raise HTTPException(
                status_code=403,
                detail="Esta cuenta es de instructor. Usa el acceso «Soy instructor».",
            )
        if nombre_rol == "Aprendiz":
            raise HTTPException(
                status_code=403,
                detail="Esta cuenta es de aprendiz. Usa el acceso «Soy aprendiz».",
            )
        raise HTTPException(
            status_code=403,
            detail="Esta cuenta no tiene rol de administrador.",
        )

    codigo, email_ok = LoginService.enviar_codigo_admin(correo)

    # Si el correo no se envió (SMTP no configurado o falló), devolvemos el
    # código una sola vez en la respuesta para que puedas entrar sin consola.
    respuesta = {
        "mensaje": (
            "Se envió un código de verificación a tu correo. Ingrésalo para completar el acceso."
            if email_ok
            else (
                "No se pudo enviar el correo. Usa el código temporal que aparece abajo "
                "(también está en los logs del backend)."
            )
        ),
        "requiere_codigo": True,
        "correo": correo,
        "email_enviado": email_ok,
    }
    if not email_ok:
        respuesta["codigo_temporal"] = codigo
    return respuesta


@router.post("/admin/verificar", response_model=LoginResponse)
def admin_verificar(datos: VerificarCodigoRequest, session: Session = Depends(get_session)):
    """Verifica el código de admin y emite el token de sesión."""
    correo = datos.correo.strip().lower()
    if not verificar_codigo(correo, datos.codigo.strip(), tipo="admin", consumir=True):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    usuario = LoginService.buscar_por_correo(session, correo)
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Cuenta no activa.")
    if not usuario.rol or usuario.rol.nombre not in ("Administrador", "Admin"):
        raise HTTPException(status_code=403, detail="No es administrador.")

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol=usuario.rol.nombre,
    )
    usuario_data = _usuario_a_dict(usuario)
    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)
