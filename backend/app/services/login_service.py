import re
from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.instructor import Instructor
from app.config.security import generar_codigo_numerico, guardar_codigo
try:
    from app.services.email_service import (
        enviar_codigo_recuperacion as mail_codigo_recuperacion,
        enviar_codigo_instructor as mail_codigo_instructor,
    )
except Exception:
    mail_codigo_recuperacion = None
    mail_codigo_instructor = None

password_hash = PasswordHash.recommended()

class LoginService:

    # Marcador: el instructor aún no ha definido su contraseña real
    PASSWORD_PENDIENTE_MARKER = "__PENDIENTE_CREAR_PASSWORD__"

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
        correo = (correo or "").strip().lower()
        codigo = generar_codigo_numerico(6)
        guardar_codigo(correo, codigo, tipo="recuperacion", expiracion_minutos=15)
        print(f"\n{'='*50}")
        print(f"[EMAIL] Código de recuperación para {correo}: {codigo}")
        print(f"{'='*50}\n")
        if mail_codigo_recuperacion:
            try:
                ok = mail_codigo_recuperacion(correo, codigo)
                if not ok:
                    print("[EMAIL] Aviso: no se envió correo de recuperación. Usa el de la consola.")
            except Exception as e:
                print(f"[EMAIL] Error recuperación: {e}")
        return codigo

    @staticmethod
    def enviar_codigo_instructor(correo: str) -> str:
        correo = (correo or "").strip().lower()
        codigo = generar_codigo_numerico(6)
        guardar_codigo(correo, codigo, tipo="instructor", expiracion_minutos=15)

        # Siempre en consola (respaldo en desarrollo)
        print(f"\n{'='*50}")
        print(f"[EMAIL] Código de verificación instructor para {correo}: {codigo}")
        print(f"{'='*50}\n")

        # Envío real si SMTP está configurado en .env
        if mail_codigo_instructor:
            try:
                ok = mail_codigo_instructor(correo, codigo)
                if not ok:
                    print("[EMAIL] Aviso: no se envió al correo del instructor. Usa el de la consola.")
            except Exception as e:
                print(f"[EMAIL] Error enviando a instructor: {e}")
        return codigo


    @staticmethod
    def instructor_necesita_crear_password(session: Session, correo: str) -> bool:
        """True si el instructor existe pero aún no ha creado su contraseña."""
        usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
        if not usuario:
            return False
        # Si la contraseña actual verifica contra el marcador, aún no la creó
        return LoginService.verificar_password(
            LoginService.PASSWORD_PENDIENTE_MARKER, usuario.contrasena
        )

    @staticmethod
    def establecer_password_instructor(session: Session, correo: str, nueva: str):
        usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
        if not usuario:
            return None, "Usuario no encontrado"
        es_segura, msg = LoginService.validar_contrasena_segura(nueva)
        if not es_segura:
            return None, msg
        usuario.contrasena = LoginService.hash_password(nueva)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario, "Contraseña creada correctamente."

    @staticmethod
    def buscar_instructor_por_correo(session: Session, correo: str):
        return session.exec(select(Instructor).where(Instructor.correo == correo)).first()