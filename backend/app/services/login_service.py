from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.models.aprendiz import Aprendiz


password_hash = PasswordHash.recommended()


class LoginService:

    @staticmethod
    def hash_password(contrasena: str) -> str:
        """
        Genera un hash seguro de la contraseña.
        """
        return password_hash.hash(contrasena)

    @staticmethod
    def verificar_password(
        contrasena: str,
        contrasena_hash: str
    ) -> bool:
        """
        Verifica si la contraseña ingresada
        corresponde al hash almacenado.
        """
        return password_hash.verify(
            contrasena,
            contrasena_hash
        )

    @staticmethod
    def validar_login(
        session: Session,
        correo: str,
        contrasena: str
    ):
        """
        Busca al aprendiz por correo y verifica
        la contraseña utilizando su hash.
        """

        aprendiz = session.exec(
            select(Aprendiz).where(
                Aprendiz.correo == correo
            )
        ).first()

        if not aprendiz:
            return None, "Correo o contraseña incorrectos"

        if not LoginService.verificar_password(
            contrasena,
            aprendiz.contrasena
        ):
            return None, "Correo o contraseña incorrectos"

        return aprendiz, "Inicio de sesión exitoso"

    @staticmethod
    def resetear_password(
        session: Session,
        correo: str,
        nueva_contrasena: str
    ):
        """
        Busca al aprendiz por correo y, si existe,
        reemplaza su contraseña por una nueva (hasheada).
        """

        aprendiz = session.exec(
            select(Aprendiz).where(
                Aprendiz.correo == correo
            )
        ).first()

        if not aprendiz:
            return None, (
                "No existe ninguna cuenta registrada con ese correo."
            )

        aprendiz.contrasena = LoginService.hash_password(
            nueva_contrasena
        )

        session.add(aprendiz)
        session.commit()
        session.refresh(aprendiz)

        return aprendiz, "Contraseña actualizada correctamente."