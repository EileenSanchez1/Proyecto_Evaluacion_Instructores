from fastapi import FastAPI

from app.config.database import create_db_and_tables

from app.routers.aprendiz_router import router as aprendiz_router
from app.routers.evaluacion_router import router as evaluacion_router
from app.routers.ficha_router import router as ficha_router
from app.routers.instructor_router import router as instructor_router
from app.routers.login_router import router as login_router
from app.routers.pregunta_router import router as pregunta_router
from app.routers.reporte_router import router as reporte_router
from app.routers.respuesta_router import router as respuesta_router


app = FastAPI(
    title="Sistema de Evaluación de Instructores",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    create_db_and_tables()


# =========================
# Routers
# =========================

app.include_router(aprendiz_router)
app.include_router(evaluacion_router)
app.include_router(ficha_router)
app.include_router(instructor_router)
app.include_router(login_router)
app.include_router(pregunta_router)
app.include_router(reporte_router)
app.include_router(respuesta_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente"
    }