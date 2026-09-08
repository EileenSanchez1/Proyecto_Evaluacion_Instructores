import re
from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.instructor import Instructor
from app.config.security import generar_codigo_numerico, guardar_codigo

password_hash = PasswordHash.recommended()

class LoginService:

    PATRON_SEGURO = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]).{8,}$')

    @staticmethod
    def hash_password(contrasena: str) -> str:
        return password_hash.hash(contrasena)

    @staticmethod
    def verificar_password(contrasena: str, contrasena_hash: str) -> bool:
        return password_hash.verify(contrasena, contrasena_hash)

    @staticmethod
    def validar_contrasena_segura(contrasena: str) -> tuple[bool, str]:
        if len(contrasena) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        if not re.search(r"[A-Z]", contrasena):
            return False, "Debe contener al menos una mayúscula."
        if not re.search(r"[a-z]", contrasena):
            return False, "Debe contener al menos una minúscula."
        if not re.search(r"\d", contrasena):
            return False, "Debe contener al menos un número."
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", contrasena):
            return False, "Debe contener al menos un carácter especial."
        return True, "Contraseña segura."

    @staticmethod
    def validar_login(session: Session, correo: str, contrasena: str):
        usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
        if not usuario:
            return None, "Correo o contraseña incorrectos"
        if not usuario.activo:
            return None, "Esta cuenta se encuentra inactiva"
        if not LoginService.verificar_password(contrasena, usuario.contrasena):
            return None, "Correo o contraseña incorrectos"
        return usuario, "Inicio de sesión exitoso"

    @staticmethod
    def buscar_por_correo(session: Session, correo: str):
        return session.exec(select(Usuario).where(Usuario.correo == correo)).first()

    @staticmethod
    def restablecer_password(session: Session, usuario: Usuario, nueva_contrasena: str):
        usuario.contrasena = LoginService.hash_password(nueva_contrasena)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario, "Contraseña actualizada correctamente."

    @staticmethod
    def enviar_codigo_recuperacion(correo: str) -> str:
        codigo = generar_codigo_numerico(6)
        guardar_codigo(correo, codigo, tipo="recuperacion", expiracion_minutos=15)
        # Aquí iría el envío real de email. Por ahora imprimimos en consola:
        print(f"\n{'='*50}")
        print(f"[EMAIL] Código de recuperación para {correo}: {codigo}")
        print(f"{'='*50}\n")
        return codigo

    @staticmethod
    def enviar_codigo_instructor(correo: str) -> str:
        codigo = generar_codigo_numerico(6)
        guardar_codigo(correo, codigo, tipo="instructor", expiracion_minutos=15)
        print(f"\n{'='*50}")
        print(f"[EMAIL] Código de verificación instructor para {correo}: {codigo}")
        print(f"{'='*50}\n")
        return codigo

    @staticmethod
    def buscar_instructor_por_correo(session: Session, correo: str):
        return session.exec(select(Instructor).where(Instructor.correo == correo)).first()