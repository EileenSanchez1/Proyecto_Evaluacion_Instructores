"""
Configuración compartida de las pruebas.

- Usa una base de datos SQLite EN MEMORIA (nunca toca Neon/PostgreSQL ni database.sqlite).
- Reemplaza el envío de correos por funciones falsas (no se usa SMTP).
"""
import os

# ---- Variables de entorno ANTES de importar la app ----
# Vaciar las de PostgreSQL para que load_dotenv() no use la BD real del .env
for _k in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"):
    os.environ[_k] = ""
os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "clave-de-pruebas-con-mas-de-32-caracteres!!"
os.environ["ALLOW_DEBUG_CODES"] = "false"
os.environ["ALLOW_SHOW_ADMIN_CODE"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

import app.models  # noqa: F401  (registra todas las tablas)
from app.config.database import get_session
from app.models.aprendiz import Aprendiz
from app.models.instructor import Instructor
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.services.login_service import LoginService

PASSWORD_OK = "Clave123!"


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture(autouse=True)
def correo_falso(monkeypatch):
    """Por defecto los correos 'se envían bien' sin salir a internet."""
    import app.services.login_service as ls

    enviados = []

    def _ok(destinatario, codigo):
        enviados.append((destinatario, codigo))
        return True

    monkeypatch.setattr(ls, "mail_codigo_recuperacion", _ok, raising=False)
    monkeypatch.setattr(ls, "mail_codigo_instructor", _ok, raising=False)
    monkeypatch.setattr(ls, "mail_codigo_admin", _ok, raising=False)
    return enviados


@pytest.fixture(autouse=True)
def limpiar_codigos():
    """Los códigos OTP viven en memoria: se limpian entre pruebas."""
    from app.config import security

    yield
    security._codigos_recuperacion.clear()
    security._codigos_instructor.clear()
    security._codigos_admin.clear()


@pytest.fixture
def client(session):
    from main import app

    app.dependency_overrides[get_session] = lambda: session
    # Sin "with": no se ejecuta el evento startup (seed sobre la BD real)
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


# ---------- Fábricas de datos ----------
@pytest.fixture
def roles(session):
    creados = {}
    for nombre in ("Administrador", "Coordinador", "Aprendiz", "Instructor"):
        r = Rol(nombre=nombre, descripcion=f"Rol {nombre}", activo=True)
        session.add(r)
        creados[nombre] = r
    session.commit()
    for r in creados.values():
        session.refresh(r)
    return creados


@pytest.fixture
def crear_usuario(session, roles):
    def _crear(correo, rol="Aprendiz", contrasena=PASSWORD_OK, activo=True):
        u = Usuario(
            nombre="Prueba",
            apellido="Test",
            correo=correo.lower(),
            contrasena=LoginService.hash_password(contrasena),
            id_rol=roles[rol].id_rol,
            activo=activo,
        )
        session.add(u)
        session.commit()
        session.refresh(u)
        return u

    return _crear


@pytest.fixture
def usuario_aprendiz(session, crear_usuario):
    u = crear_usuario("aprendiz@soy.sena.edu.co", rol="Aprendiz")
    # SQLite no exige las llaves foráneas: id_ficha / id_periodo de prueba
    a = Aprendiz(
        nombre=u.nombre, apellido=u.apellido, correo=u.correo,
        contrasena=u.contrasena, id_ficha=1, id_periodo=1, id_usuario=u.id_usuario,
    )
    session.add(a)
    session.commit()
    return u


@pytest.fixture
def usuario_admin(crear_usuario):
    return crear_usuario("admin@soy.sena.edu.co", rol="Administrador")


@pytest.fixture
def crear_instructor(session, crear_usuario):
    def _crear(correo="instructor@sena.edu.co", contrasena=PASSWORD_OK):
        u = crear_usuario(correo, rol="Instructor", contrasena=contrasena)
        i = Instructor(
            nombre="Ins", apellido="Tructor", correo=u.correo,
            telefono="3000000000", id_usuario=u.id_usuario,
        )
        session.add(i)
        session.commit()
        session.refresh(i)
        return i, u

    return _crear


@pytest.fixture
def token_de():
    from app.config.security import crear_access_token

    def _token(usuario):
        t = crear_access_token(usuario.id_usuario, usuario.correo, usuario.rol.nombre)
        return {"Authorization": f"Bearer {t}"}

    return _token
