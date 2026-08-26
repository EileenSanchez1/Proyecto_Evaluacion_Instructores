from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.config.database import engine
from app.models.aprendiz import Aprendiz


password_hash = PasswordHash.recommended()

CORREO_ADMIN = "admin@evaluacion.com"
CONTRASENA_ADMIN = "Admin12345"


def crear_admin():
    with Session(engine) as session:

        admin_existente = session.exec(
            select(Aprendiz).where(Aprendiz.correo == CORREO_ADMIN)
        ).first()

        if admin_existente:
            print("El administrador ya existe.")
            print(f"Correo: {CORREO_ADMIN}")
            return

        admin = Aprendiz(
            nombre="Administrador",
            apellido="Sistema",
            correo=CORREO_ADMIN,
            contrasena=password_hash.hash(CONTRASENA_ADMIN),
            id_ficha=1,
            es_admin=True
        )

        session.add(admin)
        session.commit()
        session.refresh(admin)

        print("Administrador creado correctamente.")
        print(f"Correo: {CORREO_ADMIN}")
        print(f"Contraseña: {CONTRASENA_ADMIN}")
        print(f"ID aprendiz: {admin.id_aprendiz}")


if __name__ == "__main__":
    crear_admin()