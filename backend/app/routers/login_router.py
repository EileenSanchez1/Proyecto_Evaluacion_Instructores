from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config.database import get_session
from app.config.security import (
    crear_access_token,
    crear_token_recuperacion,
    verificar_token_recuperacion
)
from app.schemas.login import (
    LoginRequest,
    LoginResponse,
    SolicitarRecuperacionRequest,
    RestablecerPasswordRequest
)
from app.services.login_service import LoginService
from app.models.aprendiz import Aprendiz


router = APIRouter(prefix="/login", tags=["Login"])


@router.post("/", response_model=LoginResponse)
def login(datos: LoginRequest, session: Session = Depends(get_session)):
    usuario, mensaje = LoginService.validar_login(
        session, datos.correo, datos.contrasena
    )

    if usuario is None:
        raise HTTPException(status_code=401, detail=mensaje)

    token = crear_access_token(
        id_usuario=usuario.id_usuario,
        correo=usuario.correo,
        rol=usuario.rol.nombre
    )

    usuario_data = {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre,
        "foto": usuario.foto
    }

    if usuario.rol.nombre == "Aprendiz":
        aprendiz = session.exec(
            select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)
        ).first()
        if aprendiz:
            usuario_data["id_aprendiz"] = aprendiz.id_aprendiz
            usuario_data["id_ficha"] = aprendiz.id_ficha
            usuario_data["id_periodo"] = aprendiz.id_periodo

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        usuario=usuario_data
    )


@router.post("/recuperar", response_model=dict)
def solicitar_recuperacion(
    datos: SolicitarRecuperacionRequest,
    session: Session = Depends(get_session)
):
    usuario = LoginService.buscar_por_correo(session, datos.correo)
    if usuario:
        token = crear_token_recuperacion(usuario.id_usuario, usuario.correo)
        print(
            f"[DEV] Enlace de recuperación para {usuario.correo}: "
            f"http://localhost:5173/restablecer-contrasena?token={token}"
        )
    return {
        "mensaje": (
            "Si el correo está registrado, recibirás un enlace "
            "de recuperación en unos minutos."
        )
    }


@router.post("/restablecer", response_model=dict)
def restablecer_password(
    datos: RestablecerPasswordRequest,
    session: Session = Depends(get_session)
):
    payload = verificar_token_recuperacion(datos.token)
    usuario = LoginService.buscar_por_correo(session, payload["correo"])

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    _, mensaje = LoginService.restablecer_password(
        session, usuario, datos.nueva_contrasena
    )
    return {"mensaje": mensaje}