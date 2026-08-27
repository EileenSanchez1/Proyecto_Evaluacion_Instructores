from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.models.usuario import Usuario
from app.models.rol import Rol


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
        Busca al usuario por correo (Administrador, Coordinador,
        Instructor o Aprendiz -- los 4 roles viven en Usuario) y
        verifica la contraseña con su hash.
        """

        usuario = session.exec(
            select(Usuario).where(
                Usuario.correo == correo
            )
        ).first()

        if not usuario:
            return None, "Correo o contraseña incorrectos"

        if not usuario.activo:
            return None, "Esta cuenta se encuentra inactiva"

        if not LoginService.verificar_password(
            contrasena,
            usuario.contrasena
        ):
            return None, "Correo o contraseña incorrectos"

        return usuario, "Inicio de sesión exitoso"

    @staticmethod
    def buscar_por_correo(
        session: Session,
        correo: str
    ):
        return session.exec(
            select(Usuario).where(
                Usuario.correo == correo
            )
        ).first()

    @staticmethod
    def restablecer_password(
        session: Session,
        usuario: Usuario,
        nueva_contrasena: str
    ):
        usuario.contrasena = LoginService.hash_password(
            nueva_contrasena
        )

        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        return usuario, "Contraseña actualizada correctamente."
