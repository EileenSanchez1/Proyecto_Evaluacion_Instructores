"""
Crea datos de prueba para las pruebas de carga con Locust en la base LOCAL
(SQLite: backend/database.sqlite). No toca la base del despliegue.

Crea:
  - 1 periodo activo        "CARGA-2026"
  - 1 ficha                 "CARGA-0001"
  - 19 preguntas oficiales  (si no existen)
  - 5 instructores          instructor1@sena.edu.co ... instructor5@sena.edu.co
  - 20 aprendices           aprendiz1@soy.sena.edu.co ... aprendiz20@soy.sena.edu.co
  - Asignación de los 5 instructores a la ficha en el periodo
  Contraseña de todos: Prueba123!

Uso (desde la carpeta backend, con el venv activo):
  1. Iniciar el backend una vez (uvicorn main:app --port 8000) para que cree
     las tablas y los roles; luego detenerlo con Ctrl+C.
  2. python seed_datos_prueba_carga.py
"""
import json
from datetime import date
from pathlib import Path

from sqlmodel import Session, select

from app.config.database import engine, create_db_and_tables
from app.models.aprendiz import Aprendiz
from app.models.ficha import Ficha
from app.models.ficha_instructor import FichaInstructor
from app.models.instructor import Instructor
from app.models.periodo import Periodo
from app.models.pregunta import Pregunta
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.services.login_service import LoginService

CONTRASENA = "Prueba123!"
N_INSTRUCTORES = 5
N_APRENDICES = 20


def obtener_o_crear_rol(session, nombre):
    rol = session.exec(select(Rol).where(Rol.nombre == nombre)).first()
    if not rol:
        rol = Rol(nombre=nombre, descripcion=f"Rol {nombre}", activo=True)
        session.add(rol)
        session.commit()
        session.refresh(rol)
    return rol


def obtener_o_crear_usuario(session, nombre, apellido, correo, rol, hash_clave):
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario:
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo,
                          contrasena=hash_clave, id_rol=rol.id_rol, activo=True)
    else:
        usuario.contrasena = hash_clave
        usuario.activo = True
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def main():
    url = str(engine.url)
    if not url.startswith("sqlite"):
        print(f"ALTO: el backend está conectado a {engine.url.render_as_string(hide_password=True)}")
        print("Este script solo se ejecuta sobre la base SQLite local.")
        return

    create_db_and_tables()
    hash_clave = LoginService.hash_password(CONTRASENA)

    with Session(engine) as session:
        rol_aprendiz = obtener_o_crear_rol(session, "Aprendiz")
        rol_instructor = obtener_o_crear_rol(session, "Instructor")

        # Periodo activo
        periodo = session.exec(select(Periodo).where(Periodo.nombre == "CARGA-2026")).first()
        if not periodo:
            periodo = Periodo(nombre="CARGA-2026", descripcion="Periodo para pruebas de carga",
                              fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 12, 31),
                              estado="Activo")
            session.add(periodo)
            session.commit()
            session.refresh(periodo)

        # Ficha
        ficha = session.exec(select(Ficha).where(Ficha.numero_ficha == "CARGA-0001")).first()
        if not ficha:
            ficha = Ficha(numero_ficha="CARGA-0001", programa="ADSO - Pruebas de carga",
                          descripcion="Ficha para pruebas de carga")
            session.add(ficha)
            session.commit()
            session.refresh(ficha)

        # Preguntas oficiales
        ruta = Path(__file__).resolve().parent / "app" / "data" / "preguntas_oficiales_sena.json"
        with open(ruta, encoding="utf-8") as f:
            for item in json.load(f):
                desc = item["descripcion"].strip()
                if not session.exec(select(Pregunta).where(Pregunta.descripcion == desc)).first():
                    session.add(Pregunta(descripcion=desc, orden=int(item["orden"]), estado=True))
        session.commit()

        # Instructores + asignación a la ficha
        for n in range(1, N_INSTRUCTORES + 1):
            correo = f"instructor{n}@sena.edu.co"
            usuario = obtener_o_crear_usuario(session, f"Instructor{n}", "Prueba", correo,
                                              rol_instructor, hash_clave)
            instructor = session.exec(select(Instructor).where(Instructor.correo == correo)).first()
            if not instructor:
                instructor = Instructor(nombre=f"Instructor{n}", apellido="Prueba", correo=correo,
                                        telefono="3000000000", id_usuario=usuario.id_usuario)
                session.add(instructor)
                session.commit()
                session.refresh(instructor)
            asignado = session.exec(select(FichaInstructor).where(
                FichaInstructor.id_ficha == ficha.id_ficha,
                FichaInstructor.id_instructor == instructor.id_instructor,
                FichaInstructor.id_periodo == periodo.id_periodo,
            )).first()
            if not asignado:
                session.add(FichaInstructor(id_ficha=ficha.id_ficha,
                                            id_instructor=instructor.id_instructor,
                                            id_periodo=periodo.id_periodo, activo=True))
        session.commit()

        # Aprendices
        for n in range(1, N_APRENDICES + 1):
            correo = f"aprendiz{n}@soy.sena.edu.co"
            usuario = obtener_o_crear_usuario(session, f"Aprendiz{n}", "Prueba", correo,
                                              rol_aprendiz, hash_clave)
            aprendiz = session.exec(select(Aprendiz).where(Aprendiz.correo == correo)).first()
            if not aprendiz:
                aprendiz = Aprendiz(nombre=f"Aprendiz{n}", apellido="Prueba", correo=correo,
                                    contrasena=hash_clave, id_ficha=ficha.id_ficha,
                                    id_periodo=periodo.id_periodo, id_usuario=usuario.id_usuario)
            else:
                aprendiz.contrasena = hash_clave
            session.add(aprendiz)
        session.commit()

    print("Datos de prueba listos en la base SQLite local.")
    print("Usa en locustfile.py (sección CONFIGURACIÓN):")
    print(f"  APRENDIZ:   aprendiz1@soy.sena.edu.co   / {CONTRASENA}")
    print(f"  INSTRUCTOR: instructor1@sena.edu.co     / {CONTRASENA}")


if __name__ == "__main__":
    main()
