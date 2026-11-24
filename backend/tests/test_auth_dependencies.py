"""Control de acceso por rol (get_current_user / require_roles)."""
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.config.auth_dependencies import require_roles
from app.config.database import get_session
from app.config.security import crear_access_token


def _mini_app(session):
    app = FastAPI()

    @app.get("/solo-admin", dependencies=[Depends(require_roles("Administrador"))])
    def solo_admin():
        return {"ok": True}

    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def test_sin_token_es_rechazado(session):
    r = _mini_app(session).get("/solo-admin")
    assert r.status_code in (401, 403)


def test_admin_tiene_acceso(session, usuario_admin, token_de):
    r = _mini_app(session).get("/solo-admin", headers=token_de(usuario_admin))
    assert r.status_code == 200


def test_aprendiz_no_tiene_acceso_a_ruta_de_admin(session, usuario_aprendiz, token_de):
    r = _mini_app(session).get("/solo-admin", headers=token_de(usuario_aprendiz))
    assert r.status_code == 403
    assert "Administrador" in r.json()["detail"]


def test_token_con_sub_no_numerico(session, roles):
    t = crear_access_token("abc", "x@sena.edu.co", "Administrador")
    r = _mini_app(session).get("/solo-admin", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 401


def test_usuario_inexistente(session, roles):
    t = crear_access_token(9999, "x@sena.edu.co", "Administrador")
    r = _mini_app(session).get("/solo-admin", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 401


def test_usuario_inactivo(session, crear_usuario, token_de):
    u = crear_usuario("off@soy.sena.edu.co", rol="Administrador", activo=False)
    r = _mini_app(session).get("/solo-admin", headers=token_de(u))
    assert r.status_code == 401


def test_rutas_reales_de_reportes_protegidas(client, usuario_aprendiz, token_de):
    # El dashboard de reportes es solo para Administrador / Coordinador
    r = client.get("/reportes/dashboard", headers=token_de(usuario_aprendiz))
    assert r.status_code == 403
