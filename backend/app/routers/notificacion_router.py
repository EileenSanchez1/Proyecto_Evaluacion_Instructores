from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.config.database import get_session
from app.config.auth_dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion


router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"]
)


@router.get("/", response_model=List[dict])
def listar_notificaciones(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user)
):
    statement = select(Notificacion).where(
        Notificacion.id_usuario == usuario.id_usuario
    ).order_by(Notificacion.fecha.desc())

    notificaciones = session.exec(statement).all()

    return [
        {
            "id_notificacion": n.id_notificacion,
            "titulo": n.titulo,
            "mensaje": n.mensaje,
            "tipo": n.tipo,
            "fecha": n.fecha.isoformat(),
            "leida": n.leida
        }
        for n in notificaciones
    ]


@router.patch("/{notificacion_id}/leer")
def marcar_leida(
    notificacion_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user)
):
    notificacion = session.get(Notificacion, notificacion_id)

    if not notificacion or notificacion.id_usuario != usuario.id_usuario:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notificacion.leida = True
    session.add(notificacion)
    session.commit()
    session.refresh(notificacion)

    return {"mensaje": "Notificación marcada como leída"}


@router.get("/no-leidas/count")
def contar_no_leidas(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user)
):
    statement = select(Notificacion).where(
        (Notificacion.id_usuario == usuario.id_usuario) &
        (Notificacion.leida == False)
    )

    count = len(session.exec(statement).all())

    return {"count": count}
