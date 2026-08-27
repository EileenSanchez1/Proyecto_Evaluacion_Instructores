"""
Crea el usuario administrador inicial del sistema.

CORREGIDO (Etapa 2): antes este script creaba un Aprendiz con
es_admin=True, un patrón que la Etapa 1 ya había reemplazado por
Usuario + Rol. Ahora crea directamente un Usuario con rol
"Administrador", que es como el resto del sistema (login,
require_roles, etc.) espera encontrar al admin.

Requiere que seed_roles.py ya se haya ejecutado (para que exista
el rol "Administrador").
"""

from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.config.database import engine
from app.models.rol import Rol
from app.models.usuario import Usuario


password_hash = PasswordHash.recommended()

CORREO_ADMIN = "admin@evaluacion.com"
CONTRASENA_ADMIN = "Admin12345"


def crear_admin():
    with Session(engine) as session:

        admin_existente = session.exec(
            select(Usuario).where(Usuario.correo == CORREO_ADMIN)
        ).first()

        if admin_existente:
            print("El administrador ya existe.")
            print(f"Correo: {CORREO_ADMIN}")
            return

        rol_admin = session.exec(
            select(Rol).where(Rol.nombre == "Administrador")
        ).first()

        if not rol_admin:
            raise RuntimeError(
                "El rol 'Administrador' no existe todavía. "
                "Ejecuta primero seed_roles.py"
            )

        admin = Usuario(
            nombre="Administrador",
            apellido="Sistema",
            correo=CORREO_ADMIN,
            contrasena=password_hash.hash(CONTRASENA_ADMIN),
            id_rol=rol_admin.id_rol
        )

        session.add(admin)
        session.commit()
        session.refresh(admin)

        print("Administrador creado correctamente.")
        print(f"Correo: {CORREO_ADMIN}")
        print(f"Contraseña: {CONTRASENA_ADMIN}")
        print(f"ID usuario: {admin.id_usuario}")


if __name__ == "__main__":
    crear_admin()
