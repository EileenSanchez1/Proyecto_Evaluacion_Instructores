from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.config.database import get_session
from app.config.security import decodificar_token
from app.models.usuario import Usuario
from app.models.rol import Rol

bearer_scheme = HTTPBearer()


def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Decodifica el JWT y carga el Usuario real desde BD con su rol
    (evita N+1 / lazy load fallido en dependencias).
    """
    payload = decodificar_token(credenciales.credentials)
    id_usuario = payload.get("sub")

    try:
        uid = int(id_usuario)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido.",
        )

    statement = (
        select(Usuario)
        .where(Usuario.id_usuario == uid)
        .options(selectinload(Usuario.rol))
    )
    usuario = session.exec(statement).first()

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido o inactivo.",
        )

    return usuario


def require_roles(*roles_permitidos: str):
    """
    Dependencia factory para proteger endpoints por rol.

    Uso:
        @router.post("/", dependencies=[Depends(require_roles("Administrador"))])
        @router.get("/", dependencies=[Depends(require_roles("Administrador", "Coordinador"))])
    """

    def verificador(
        usuario: Usuario = Depends(get_current_user),
    ) -> Usuario:
        rol_nombre = None
        if usuario.rol is not None:
            rol_nombre = usuario.rol.nombre
        if rol_nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para realizar esta acción. "
                    f"Rol requerido: {', '.join(roles_permitidos)}."
                ),
            )
        return usuario

    return verificador
