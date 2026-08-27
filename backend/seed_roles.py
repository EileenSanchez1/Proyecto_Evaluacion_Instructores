from sqlmodel import Session, select

from app.config.database import engine
from app.models.rol import Rol


ROLES = [
    {
        "nombre": "Administrador",
        "descripcion": "Administra completamente el sistema."
    },
    {
        "nombre": "Coordinador",
        "descripcion": "Gestiona fichas, instructores, evaluaciones y reportes."
    },
    {
        "nombre": "Instructor",
        "descripcion": "Consulta la información y resultados correspondientes."
    },
    {
        "nombre": "Aprendiz",
        "descripcion": "Realiza evaluaciones de sus instructores."
    },
]


def seed_roles():
    with Session(engine) as session:

        for datos in ROLES:

            rol_existente = session.exec(
                select(Rol).where(
                    Rol.nombre == datos["nombre"]
                )
            ).first()

            if rol_existente:
                print(f"Ya existe: {datos['nombre']}")
                continue

            rol = Rol(**datos)

            session.add(rol)

            print(f"Creado: {datos['nombre']}")

        session.commit()


if __name__ == "__main__":
    seed_roles()
    print("Roles procesados correctamente.")