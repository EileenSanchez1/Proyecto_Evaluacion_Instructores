from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.config.database import get_session
from app.config.security import decodificar_token
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer()


def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> Usuario:
    """
    Decodifica el JWT enviado en el header Authorization: Bearer <token>
    y devuelve el Usuario real desde la base de datos (no solo lo que
    diga el token, para respetar cambios de rol/estado hechos después
    de haberse emitido el token).
    """

    payload = decodificar_token(credenciales.credentials)

    id_usuario = payload.get("sub")

    usuario = session.get(Usuario, int(id_usuario))

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido o inactivo."
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
        usuario: Usuario = Depends(get_current_user)
    ) -> Usuario:

        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para realizar esta acción. "
                    f"Rol requerido: {', '.join(roles_permitidos)}."
                )
            )

        return usuario

    return verificador
