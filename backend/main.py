from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config.database import create_db_and_tables, engine

from app.routers.aprendiz_router import router as aprendiz_router
from app.routers.resultado_aprendizaje_router import router as resultado_aprendizaje_router
from app.routers.evaluacion_router import router as evaluacion_router
from app.routers.ficha_router import router as ficha_router
from app.routers.ficha_instructor_router import router as ficha_instructor_router
from app.routers.instructor_router import router as instructor_router
from app.routers.login_router import router as login_router
from app.routers.pregunta_router import router as pregunta_router
from app.routers.reporte_router import router as reporte_router
from app.routers.respuesta_router import router as respuesta_router
from app.routers.periodo_router import router as periodo_router
from app.routers.notificacion_router import router as notificacion_router
from app.routers.novedad_router import router as novedad_router
from app.routers.admin_usuario_router import router as admin_usuario_router


def ensure_extra_columns():
    """Columnas nuevas sin romper BD existente (Neon/local)."""
    from sqlalchemy import text
    from app.config.database import engine
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS observacion_general VARCHAR(1000)"
            ))
            # Horario: enlace a Resultado de Aprendizaje + ambiente
            conn.execute(text(
                "ALTER TABLE horarios ADD COLUMN IF NOT EXISTS id_resultado INTEGER"
            ))
            conn.execute(text(
                "ALTER TABLE horarios ADD COLUMN IF NOT EXISTS ambiente VARCHAR(80)"
            ))
            # Asignación ficha-instructor: RA que dicta en esa ficha/periodo
            conn.execute(text(
                "ALTER TABLE ficha_instructor ADD COLUMN IF NOT EXISTS id_resultado INTEGER"
            ))
            # Soft-delete de asignación instructor↔ficha (si falta, listar/crear falla y el
            # navegador lo reporta como CORS porque la respuesta 500 no trae headers CORS).
            conn.execute(text(
                "ALTER TABLE ficha_instructor ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE"
            ))
            # Rellenar nulos por si la columna existía sin default en filas viejas
            try:
                conn.execute(text(
                    "UPDATE ficha_instructor SET activo = TRUE WHERE activo IS NULL"
                ))
            except Exception:
                pass
            # Instructor: vinculación PLANTA / CONTRATO (Excel oficial SENA)
            try:
                conn.execute(text(
                    "ALTER TABLE instructores ADD COLUMN IF NOT EXISTS planta_contrato VARCHAR(20)"
                ))
            except Exception:
                # SQLite no soporta IF NOT EXISTS en ALTER: intentar sin él
                try:
                    conn.execute(text(
                        "ALTER TABLE instructores ADD COLUMN planta_contrato VARCHAR(20)"
                    ))
                except Exception:
                    pass

            # Índices de rendimiento (idempotentes en PostgreSQL)
            for stmt in (
                "CREATE INDEX IF NOT EXISTS ix_evaluaciones_aprendiz ON evaluaciones (id_aprendiz)",
                "CREATE INDEX IF NOT EXISTS ix_evaluaciones_instructor ON evaluaciones (id_instructor)",
                "CREATE INDEX IF NOT EXISTS ix_evaluaciones_periodo ON evaluaciones (id_periodo)",
                "CREATE INDEX IF NOT EXISTS ix_evaluaciones_estado ON evaluaciones (estado)",
                "CREATE INDEX IF NOT EXISTS ix_evaluaciones_aip ON evaluaciones (id_aprendiz, id_instructor, id_periodo)",
                "CREATE INDEX IF NOT EXISTS ix_respuestas_evaluacion ON respuestas (id_evaluacion)",
                "CREATE INDEX IF NOT EXISTS ix_respuestas_instructor ON respuestas (id_instructor)",
                "CREATE INDEX IF NOT EXISTS ix_ficha_instructor_activo ON ficha_instructor (id_ficha, id_periodo, activo)",
            ):
                try:
                    conn.execute(text(stmt))
                except Exception:
                    pass
    except Exception as e:
        print(f"[schema] Aviso ensure_extra_columns: {e}")


app = FastAPI(
    title="Sistema de Evaluación de Instructores",
    version="1.0.0"
)

# =========================
# CORS (configurable por entorno)
# =========================
# CORS_ORIGINS = lista separada por comas. Ej:
#   CORS_ORIGINS=https://evaluacion.sena.edu.co,https://www.sena.edu.co
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_cors_env = os.getenv("CORS_ORIGINS", "").strip()
if _cors_env:
    allow_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
else:
    allow_origins = _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =========================
# STARTUP - Auto seed roles + admin
# =========================
@app.on_event("startup")
def startup():
    create_db_and_tables()
    ensure_extra_columns()
    _seed_roles_y_admin()

def _seed_roles_y_admin():
    from sqlmodel import Session, select
    from pwdlib import PasswordHash
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    password_hash = PasswordHash.recommended()

    with Session(engine) as session:
        roles_requeridos = ["Administrador", "Coordinador", "Aprendiz", "Instructor"]
        for nombre in roles_requeridos:
            existe = session.exec(select(Rol).where(Rol.nombre == nombre)).first()
            if not existe:
                session.add(Rol(nombre=nombre, descripcion=f"Rol {nombre}", activo=True))
        session.commit()

        admin_rol = session.exec(select(Rol).where(Rol.nombre == "Administrador")).first()
        if admin_rol:
            admin = session.exec(select(Usuario).where(Usuario.correo == "admin@sena.edu.co")).first()
            if not admin:
                session.add(Usuario(
                    nombre="Admin",
                    apellido="Sistema",
                    correo="admin@sena.edu.co",
                    contrasena=password_hash.hash(os.getenv("ADMIN_INITIAL_PASSWORD", "Admin123!")),
                    id_rol=admin_rol.id_rol,
                    activo=True
                ))
                session.commit()


# =========================
# Healthcheck (datacenter / docker)
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "service": "evaluacion-instructores", "version": "1.0.0"}

# =========================
# Routers
# =========================
app.include_router(login_router)
app.include_router(aprendiz_router)
app.include_router(resultado_aprendizaje_router)
app.include_router(evaluacion_router)
app.include_router(ficha_router)
app.include_router(ficha_instructor_router)
app.include_router(instructor_router)
app.include_router(pregunta_router)
app.include_router(reporte_router)
app.include_router(respuesta_router)
app.include_router(periodo_router)
app.include_router(notificacion_router)
app.include_router(novedad_router)
app.include_router(admin_usuario_router)

# =========================
# Static files
# =========================
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "app", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")