"""
Ayuda para las pruebas de carga: muestra qué aprendices e instructores existen
en la base de datos que usa el backend y, opcionalmente, les asigna una
contraseña conocida para usarla en locustfile.py.

Uso (desde la carpeta backend, con el venv activo):

    # 1) Solo listar (no cambia nada)
    python usuarios_prueba_carga.py

    # 2) Asignar contraseña conocida a un usuario de prueba
    python usuarios_prueba_carga.py correo@soy.sena.edu.co Prueba123!

IMPORTANTE: la opción 2 cambia la contraseña de ese usuario. Úsala solo con
cuentas de prueba y en la base de datos local, nunca con usuarios reales.
"""
import sys

from sqlmodel import Session, select

from app.config.database import engine
from app.models.aprendiz import Aprendiz
from app.models.instructor import Instructor
from app.models.usuario import Usuario
from app.models.periodo import Periodo
from app.models.ficha_instructor import FichaInstructor
from app.services.login_service import LoginService


def listar(session):
    print(f"\nBase de datos en uso: {engine.url.render_as_string(hide_password=True)}\n")

    print("=== APRENDICES (para APRENDIZ_CORREO) ===")
    aprendices = session.exec(select(Aprendiz)).all()
    if not aprendices:
        print("  (no hay aprendices)")
    for a in aprendices[:30]:
        usuario = session.get(Usuario, a.id_usuario) if a.id_usuario else None
        periodo = session.get(Periodo, a.id_periodo) if a.id_periodo else None
        n_instr = len(session.exec(
            select(FichaInstructor).where(FichaInstructor.id_ficha == a.id_ficha,
                                          FichaInstructor.id_periodo == a.id_periodo)
        ).all())
        avisos = []
        if not usuario:
            avisos.append("SIN USUARIO VINCULADO (no puede iniciar sesión)")
        elif not usuario.activo:
            avisos.append("INACTIVO")
        if not periodo or str(periodo.estado).lower() != "activo":
            avisos.append("periodo no activo")
        if n_instr == 0:
            avisos.append("ficha sin instructores asignados")
        estado = "OK" if not avisos else " / ".join(avisos)
        print(f"  {a.correo:<45} ficha={a.id_ficha} periodo={a.id_periodo} "
              f"instructores={n_instr}  -> {estado}")

    print("\n=== INSTRUCTORES (para INSTRUCTOR_CORREO) ===")
    instructores = session.exec(select(Instructor)).all()
    if not instructores:
        print("  (no hay instructores)")
    for i in instructores[:30]:
        usuario = session.exec(select(Usuario).where(Usuario.correo == i.correo)).first()
        if not usuario:
            estado = "SIN USUARIO (no puede iniciar sesión)"
        elif not usuario.activo:
            estado = "INACTIVO"
        elif LoginService.instructor_necesita_crear_password(session, i.correo):
            estado = "primer acceso pendiente (sin contraseña)"
        else:
            estado = "OK"
        print(f"  {i.correo:<45} -> {estado}")
    print("\nElige un aprendiz y un instructor marcados como OK.")


def asignar_clave(session, correo, clave):
    correo = correo.strip().lower()
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()
    if not usuario:
        print(f"No existe un usuario con el correo {correo}")
        return
    confirmar = input(f"Se cambiará la contraseña de {correo}. ¿Continuar? (s/n): ")
    if confirmar.strip().lower() != "s":
        print("Cancelado.")
        return
    LoginService.restablecer_password(session, usuario, clave)
    # Mantener sincronizada la tabla aprendices, igual que hace el backend
    aprendiz = session.exec(select(Aprendiz).where(Aprendiz.id_usuario == usuario.id_usuario)).first()
    if aprendiz:
        aprendiz.contrasena = usuario.contrasena
        session.add(aprendiz)
        session.commit()
    print(f"Listo: {correo} ahora tiene la contraseña indicada.")


if __name__ == "__main__":
    with Session(engine) as s:
        if len(sys.argv) == 3:
            asignar_clave(s, sys.argv[1], sys.argv[2])
        else:
            listar(s)
