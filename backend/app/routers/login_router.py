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
)
from app.services.login_service import LoginService
from app.models.aprendiz import Aprendiz
from app.models.usuario import Usuario
from app.models.rol import Rol

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
    # Validar contraseña segura antes de intentar login
    es_segura, msg = LoginService.validar_contrasena_segura(datos.contrasena)
    if not es_segura:
        raise HTTPException(status_code=400, detail=f"Contraseña no cumple requisitos: {msg}")

    usuario, mensaje = LoginService.validar_login(session, datos.correo, datos.contrasena)
    if usuario is None:
        raise HTTPException(status_code=401, detail=mensaje)

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol=usuario.rol.nombre
    )

    usuario_data = _usuario_a_dict(usuario)

    if usuario.rol.nombre == "Aprendiz":
        aprendiz = session.exec(select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)).first()
        if aprendiz:
            usuario_data["id_aprendiz"] = aprendiz.id_aprendiz
            usuario_data["id_ficha"] = aprendiz.id_ficha
            usuario_data["id_periodo"] = getattr(aprendiz, "id_periodo", None)

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)

# =========================
# RECUPERACIÓN POR CÓDIGO
# =========================
@router.post("/recuperar", response_model=dict)
def solicitar_recuperacion(datos: SolicitarRecuperacionRequest, session: Session = Depends(get_session)):
    usuario = LoginService.buscar_por_correo(session, datos.correo)
    if usuario:
        LoginService.enviar_codigo_recuperacion(usuario.correo)
    return {"mensaje": "Si el correo está registrado, recibirás un código de verificación en unos minutos."}

@router.post("/verificar-codigo", response_model=dict)
def verificar_codigo_recuperacion(datos: VerificarCodigoRequest):
    if not verificar_codigo(datos.correo, datos.codigo, tipo="recuperacion"):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")
    return {"mensaje": "Código verificado correctamente.", "valido": True}

@router.post("/restablecer", response_model=dict)
def restablecer_password(datos: RestablecerPasswordRequest, session: Session = Depends(get_session)):
    # Validar contraseña segura
    es_segura, msg = LoginService.validar_contrasena_segura(datos.nueva_contrasena)
    if not es_segura:
        raise HTTPException(status_code=400, detail=f"La contraseña no es segura: {msg}")

    if not verificar_codigo(datos.correo, datos.codigo, tipo="recuperacion"):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    usuario = LoginService.buscar_por_correo(session, datos.correo)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    _, mensaje = LoginService.restablecer_password(session, usuario, datos.nueva_contrasena)
    limpiar_codigo(datos.correo, tipo="recuperacion")
    return {"mensaje": mensaje}


# =========================
# LOGIN INSTRUCTOR (2FA + primer acceso)
# =========================
@router.post("/instructor/iniciar", response_model=dict)
def instructor_iniciar(datos: InstructorCorreoRequest, session: Session = Depends(get_session)):
    """Paso 0: solo correo. Indica si debe crear contraseña o ya puede iniciar."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="El correo debe ser institucional (@sena.edu.co).")

    instructor = LoginService.buscar_instructor_por_correo(session, correo)
    if not instructor:
        raise HTTPException(status_code=404, detail="No hay un instructor registrado con ese correo.")

    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Cuenta de instructor no activa.")

    necesita = LoginService.instructor_necesita_crear_password(session, correo)

    # Enviar código siempre (para crear password o para login)
    LoginService.enviar_codigo_instructor(correo)

    if necesita:
        return {
            "mensaje": "Primer acceso: se envió un código a tu correo. Crea tu contraseña.",
            "requiere_crear_password": True,
            "requiere_codigo": True,
        }
    return {
        "mensaje": "Se envió un código a tu correo. Ingresa tu contraseña y el código.",
        "requiere_crear_password": False,
        "requiere_codigo": True,
    }


@router.post("/instructor/crear-password", response_model=LoginResponse)
def instructor_crear_password(datos: InstructorCrearPasswordRequest, session: Session = Depends(get_session)):
    """Primer acceso: verifica código OTP y establece la contraseña definitiva."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="Correo inválido.")

    if not verificar_codigo(correo, datos.codigo, tipo="instructor"):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    if not LoginService.instructor_necesita_crear_password(session, correo):
        raise HTTPException(status_code=400, detail="Esta cuenta ya tiene contraseña. Usa el login normal.")

    usuario, mensaje = LoginService.establecer_password_instructor(session, correo, datos.nueva_contrasena)
    if not usuario:
        raise HTTPException(status_code=400, detail=mensaje)

    limpiar_codigo(correo, tipo="instructor")

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol="Instructor",
    )
    usuario_data = _usuario_a_dict(usuario)
    instructor = LoginService.buscar_instructor_por_correo(session, correo)
    if instructor:
        usuario_data["id_instructor"] = instructor.id_instructor

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)


@router.post("/instructor", response_model=dict)
def login_instructor_paso1(datos: LoginInstructorRequest, session: Session = Depends(get_session)):
    """Login normal instructor: correo + contraseña → envía código OTP."""
    correo = datos.correo.strip().lower()
    if not correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="El correo debe ser institucional (@sena.edu.co).")

    instructor = LoginService.buscar_instructor_por_correo(session, correo)
    if not instructor:
        raise HTTPException(status_code=401, detail="Instructor no encontrado.")

    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Instructor no tiene cuenta de usuario activa.")

    if LoginService.instructor_necesita_crear_password(session, correo):
        raise HTTPException(
            status_code=400,
            detail="Debes crear tu contraseña primero. Usa el flujo de primer acceso (solo correo).",
        )

    if not LoginService.verificar_password(datos.contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    LoginService.enviar_codigo_instructor(correo)
    return {"mensaje": "Se envió un código de verificación a tu correo institucional.", "requiere_codigo": True}


@router.post("/instructor/verificar", response_model=LoginResponse)
def login_instructor_paso2(datos: VerificarCodigoInstructorRequest, session: Session = Depends(get_session)):
    if not datos.correo.endswith("@sena.edu.co"):
        raise HTTPException(status_code=400, detail="Correo inválido.")

    if not verificar_codigo(datos.correo, datos.codigo, tipo="instructor"):
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    usuario = session.exec(select(Usuario).where(Usuario.correo == datos.correo)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    limpiar_codigo(datos.correo, tipo="instructor")

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol="Instructor",
    )

    usuario_data = _usuario_a_dict(usuario)
    instructor = LoginService.buscar_instructor_por_correo(session, datos.correo)
    if instructor:
        usuario_data["id_instructor"] = instructor.id_instructor

    return LoginResponse(access_token=token, token_type="bearer", usuario=usuario_data)
