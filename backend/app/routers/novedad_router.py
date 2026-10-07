from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List
from app.config.database import get_session
from app.config.auth_dependencies import require_roles
from app.models.novedad import Novedad
from app.schemas.novedad import NovedadCreate, NovedadRead, NovedadUpdate
from app.services.email_service import enviar_novedad_resuelta

router = APIRouter(prefix="/novedades", tags=["Novedades"])


@router.post("/", response_model=dict)
def crear_novedad(datos: NovedadCreate, session: Session = Depends(get_session)):
    mensaje = (datos.mensaje or "").strip()
    palabras = [p for p in mensaje.split() if p]
    if len(palabras) < 2 or len(mensaje) < 10:
        raise HTTPException(
            status_code=400,
            detail="El mensaje debe tener al menos 2 palabras y 10 caracteres.",
        )
    novedad = Novedad(**datos.model_dump())
    session.add(novedad)
    session.commit()
    session.refresh(novedad)
    return {
        "mensaje": "Novedad enviada correctamente",
        "id_novedad": novedad.id_novedad,
    }


@router.get(
    "/no-leidas/count",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def contar_no_leidas(session: Session = Depends(get_session)):
    total = session.exec(
        select(func.count()).select_from(Novedad).where(Novedad.leido == False)  # noqa: E712
    ).one()
    return {"count": int(total or 0)}


@router.get(
    "/",
    response_model=List[NovedadRead],
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def listar_novedades(session: Session = Depends(get_session)):
    return session.exec(select(Novedad).order_by(Novedad.fecha.desc())).all()


@router.patch(
    "/{novedad_id}/leer",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def marcar_leida(novedad_id: int, session: Session = Depends(get_session)):
    novedad = session.get(Novedad, novedad_id)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    novedad.leido = True
    session.add(novedad)
    session.commit()
    return {"mensaje": "Novedad marcada como leída"}


@router.post(
    "/{novedad_id}/resolver",
    dependencies=[Depends(require_roles("Administrador", "Coordinador"))],
)
def resolver_novedad(novedad_id: int, session: Session = Depends(get_session)):
    """
    Marca la novedad como leída/solucionada y envía correo al aprendiz
    informando que ya fue atendida.
    """
    novedad = session.get(Novedad, novedad_id)
    if not novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")

    novedad.leido = True
    session.add(novedad)
    session.commit()

    correo = (novedad.correo or "").strip()
    if not correo:
        return {
            "mensaje": "Novedad marcada como solucionada, pero no tenía correo para notificar.",
            "correo_enviado": False,
        }

    nombre = f"{novedad.nombre} {novedad.apellido}".strip() or "Aprendiz"
    ok = enviar_novedad_resuelta(
        destinatario=correo,
        nombre=nombre,
        mensaje_original=novedad.mensaje,
    )
    if ok:
        return {
            "mensaje": f"Novedad solucionada. Se notificó a {correo}.",
            "correo_enviado": True,
        }
    return {
        "mensaje": (
            "Novedad marcada como solucionada, pero no se pudo enviar el correo "
            "(revisa SMTP en .env)."
        ),
        "correo_enviado": False,
    }
