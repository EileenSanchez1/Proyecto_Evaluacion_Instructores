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