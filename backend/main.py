from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config.database import create_db_and_tables, engine

from app.routers.aprendiz_router import router as aprendiz_router
from app.routers.competencia_router import router as competencia_router
from app.routers.evaluacion_router import router as evaluacion_router
from app.routers.ficha_router import router as ficha_router
from app.routers.ficha_instructor_router import router as ficha_instructor_router
from app.routers.horario_router import router as horario_router
from app.routers.instructor_router import router as instructor_router
from app.routers.login_router import router as login_router
from app.routers.pregunta_router import router as pregunta_router
from app.routers.reporte_router import router as reporte_router
from app.routers.respuesta_router import router as respuesta_router
from app.routers.periodo_router import router as periodo_router
from app.routers.notificacion_router import router as notificacion_router


app = FastAPI(
    title="Sistema de Evaluación de Instructores",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# STARTUP - Auto seed roles + admin
# =========================

@app.on_event("startup")
def startup():
    create_db_and_tables()
    _seed_roles_y_admin()


def _seed_roles_y_admin():
    """Crea roles y usuario admin automáticamente si no existen.
    Ya NO necesitas ejecutar seed_roles.py ni seed_admin.py manualmente."""
    from sqlmodel import Session, select
    from pwdlib import PasswordHash
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    password_hash = PasswordHash.recommended()

    with Session(engine) as session:
        # 1) Crear roles si no existen
        roles_data = [
            {"nombre": "Administrador", "descripcion": "Administra completamente el sistema."},
            {"nombre": "Coordinador", "descripcion": "Gestiona fichas, instructores, evaluaciones y reportes."},
            {"nombre": "Instructor", "descripcion": "Consulta la información y resultados correspondientes."},
            {"nombre": "Aprendiz", "descripcion": "Realiza evaluaciones de sus instructores."},
        ]

        for datos in roles_data:
            existente = session.exec(
                select(Rol).where(Rol.nombre == datos["nombre"])
            ).first()
            if not existente:
                session.add(Rol(**datos))
                print(f"✅ Rol creado: {datos['nombre']}")

        session.commit()

        # 2) Crear admin si no existe
        CORREO_ADMIN = "admin@evaluacion.com"
        CONTRASENA_ADMIN = "Admin12345"

        admin_existente = session.exec(
            select(Usuario).where(Usuario.correo == CORREO_ADMIN)
        ).first()

        if not admin_existente:
            rol_admin = session.exec(
                select(Rol).where(Rol.nombre == "Administrador")
            ).first()

            if rol_admin:
                admin = Usuario(
                    nombre="Administrador",
                    apellido="Sistema",
                    correo=CORREO_ADMIN,
                    contrasena=password_hash.hash(CONTRASENA_ADMIN),
                    id_rol=rol_admin.id_rol
                )
                session.add(admin)
                session.commit()
                print(f"✅ Admin creado: {CORREO_ADMIN} / {CONTRASENA_ADMIN}")


# =========================
# RUTA PRINCIPAL
# =========================

@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente"
    }


# =========================
# ROUTERS
# =========================

app.include_router(aprendiz_router)
app.include_router(competencia_router)
app.include_router(evaluacion_router)
app.include_router(ficha_router)
app.include_router(ficha_instructor_router)
app.include_router(horario_router)
app.include_router(instructor_router)
app.include_router(login_router)
app.include_router(pregunta_router)
app.include_router(reporte_router)
app.include_router(respuesta_router)
app.include_router(periodo_router)
app.include_router(notificacion_router)

# =========================
# ARCHIVOS ESTATICOS (fotos)
# =========================
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "app", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
