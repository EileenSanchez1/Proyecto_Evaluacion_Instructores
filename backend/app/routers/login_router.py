from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.config.database import get_session
from app.schemas.login import LoginRequest, RecuperarPasswordRequest
from app.schemas.aprendiz import AprendizRead
from app.services.login_service import LoginService


router = APIRouter(
    prefix="/login",
    tags=["Login"]
)


@router.post("/", response_model=dict)
def login(
    datos: LoginRequest,
    session: Session = Depends(get_session)
):
    aprendiz, mensaje = LoginService.validar_login(
        session,
        datos.correo,
        datos.contrasena
    )

    if aprendiz is None:
        raise HTTPException(
            status_code=401,
            detail=mensaje
        )

    aprendiz_data = AprendizRead.model_validate(
        aprendiz
    )

    return {
        "mensaje": mensaje,
        "aprendiz": aprendiz_data
    }


@router.post("/recuperar", response_model=dict)
def recuperar_password(
    datos: RecuperarPasswordRequest,
    session: Session = Depends(get_session)
):
    aprendiz, mensaje = LoginService.resetear_password(
        session,
        datos.correo,
        datos.nueva_contrasena
    )

    if aprendiz is None:
        raise HTTPException(
            status_code=404,
            detail=mensaje
        )

    return {
        "mensaje": mensaje
    }