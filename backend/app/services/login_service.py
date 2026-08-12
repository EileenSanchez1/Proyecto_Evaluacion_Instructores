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