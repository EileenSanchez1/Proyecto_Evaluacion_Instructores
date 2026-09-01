from typing import Optional

from sqlmodel import Session

from app.models.auditoria import Auditoria


class AuditoriaService:

    @staticmethod
    def registrar(
        session: Session,
        accion: str,
        modulo: str,
        descripcion: str,
        id_usuario: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> Auditoria:

        registro = Auditoria(
            id_usuario=id_usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            ip_address=ip_address
        )

        session.add(registro)
        session.commit()
        session.refresh(registro)

        return registro
