"""
Migra los Aprendiz e Instructor existentes hacia la tabla Usuario.

- No borra ni modifica Aprendiz.contrasena / Instructor (siguen intactos).
- Es seguro volver a ejecutarlo: si un Aprendiz/Instructor ya tiene
  id_usuario asignado, se salta.
- Los instructores no tenían contraseña propia, así que se les genera
  una temporal que debe cambiarse por el flujo de "recuperar contraseña"
  (HU-004) en cuanto esté listo.
"""

import secrets

from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.config.database import engine
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.aprendiz import Aprendiz
from app.models.instructor import Instructor


password_hash = PasswordHash.recommended()


def obtener_rol(session: Session, nombre: str) -> Rol:
    rol = session.exec(
        select(Rol).where(Rol.nombre == nombre)
    ).first()

    if not rol:
        raise RuntimeError(
            f"El rol '{nombre}' no existe todavía. "
            "Ejecuta primero seed_roles.py"
        )

    return rol


def migrar_aprendices(session: Session):
    rol_admin = obtener_rol(session, "Administrador")
    rol_aprendiz = obtener_rol(session, "Aprendiz")

    aprendices = session.exec(select(Aprendiz)).all()

    for aprendiz in aprendices:

        if aprendiz.id_usuario:
            print(f"Ya migrado: {aprendiz.correo}")
            continue

        # getattr con default False: "es_admin" se eliminó del modelo
        # Aprendiz en la Etapa 2 (quedaba como residuo del patrón
        # anterior a la Etapa 1). Este getattr solo evita que el script
        # reviente si alguien lo corre contra una BD vieja que aún
        # tenga esa columna; en una BD nueva, todo Aprendiz será
        # rol_aprendiz salvo que ya lo hayas migrado a mano.
        rol_asignado = (
            rol_admin if getattr(aprendiz, "es_admin", False)
            else rol_aprendiz
        )

        usuario = Usuario(
            nombre=aprendiz.nombre,
            apellido=aprendiz.apellido,
            correo=aprendiz.correo,
            # Reutilizamos el hash ya existente, no se re-hashea.
            contrasena=aprendiz.contrasena,
            id_rol=rol_asignado.id_rol
        )

        session.add(usuario)
        session.flush()  # para obtener usuario.id_usuario

        aprendiz.id_usuario = usuario.id_usuario
        session.add(aprendiz)

        print(
            f"Migrado aprendiz: {aprendiz.correo} "
            f"-> rol {rol_asignado.nombre}"
        )

    session.commit()


def migrar_instructores(session: Session):
    rol_instructor = obtener_rol(session, "Instructor")

    instructores = session.exec(select(Instructor)).all()

    for instructor in instructores:

        if instructor.id_usuario:
            print(f"Ya migrado: {instructor.correo}")
            continue

        clave_temporal = secrets.token_urlsafe(9)

        usuario = Usuario(
            nombre=instructor.nombre,
            apellido=instructor.apellido,
            correo=instructor.correo,
            contrasena=password_hash.hash(clave_temporal),
            id_rol=rol_instructor.id_rol
        )

        session.add(usuario)
        session.flush()

        instructor.id_usuario = usuario.id_usuario
        session.add(instructor)

        print(
            f"Migrado instructor: {instructor.correo} "
            f"-> clave temporal: {clave_temporal}"
        )

    session.commit()


if __name__ == "__main__":
    with Session(engine) as session:
        migrar_aprendices(session)
        migrar_instructores(session)

    print("\nMigración completada.")
    print(
        "IMPORTANTE: guarda las claves temporales de instructores "
        "que se imprimieron arriba; no se guardan en ningún otro lado."
    )
