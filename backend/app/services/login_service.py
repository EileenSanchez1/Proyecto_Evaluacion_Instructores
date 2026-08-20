<<<<<<< HEAD
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
=======
from sqlmodel import Session
from typing import Optional, Tuple
from app.repositories.aprendiz_repository import AprendizRepository


class LoginService:
    @staticmethod
    def validar_login(session: Session, correo: str, contrasena: str) -> Tuple[Optional[dict], str]:
        """
        Valida las credenciales de un aprendiz.
        Retorna: (datos_del_aprendiz, mensaje)
        """
        aprendiz = AprendizRepository.buscar_por_correo(session, correo)
        if not aprendiz:
            return None, "Correo o contraseña incorrectos"

        if aprendiz.contrasena != contrasena:
            return None, "Correo o contraseña incorrectos"

        return {
            "id_aprendiz": aprendiz.id_aprendiz,
            "nombre": aprendiz.nombre,
            "apellido": aprendiz.apellido,
            "correo": aprendiz.correo,
            "id_ficha": aprendiz.id_ficha
        }, "Login exitoso"
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
