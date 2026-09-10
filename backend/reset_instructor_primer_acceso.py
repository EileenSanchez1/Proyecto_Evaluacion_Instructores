"""
Pone instructores en estado de PRIMER ACCESO.

Uso (desde carpeta backend, con venv activo):
  python reset_instructor_primer_acceso.py
  python reset_instructor_primer_acceso.py ulda@sena.edu.co
"""
import sys
from sqlmodel import Session, select

from app.config.database import engine
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.services.login_service import LoginService


def main():
    correo_filtro = (sys.argv[1] if len(sys.argv) > 1 else "").strip().lower()

    with Session(engine) as session:
        rol = session.exec(select(Rol).where(Rol.nombre == "Instructor")).first()
        if not rol:
            print("No existe el rol Instructor.")
            return

        q = select(Usuario).where(Usuario.id_rol == rol.id_rol)
        usuarios = session.exec(q).all()

        if correo_filtro:
            usuarios = [u for u in usuarios if u.correo == correo_filtro or correo_filtro in u.correo]

        if not usuarios:
            print("No se encontraron instructores" + (f" con '{correo_filtro}'" if correo_filtro else ""))
            return

        for u in usuarios:
            u.contrasena = LoginService.hash_password(LoginService.PASSWORD_PENDIENTE_MARKER)
            session.add(u)
            print(f"OK primer acceso pendiente: {u.correo}")

        session.commit()
        print(f"\nListo. {len(usuarios)} instructor(es).")
        print("En Soy instructor → correo → debe pedir código (consola) y crear contraseña.")


if __name__ == "__main__":
    main()
