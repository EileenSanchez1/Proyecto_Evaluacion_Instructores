from fastapi import FastAPI

from app.config.database import create_db_and_tables

app = FastAPI(
    title="Sistema de Evaluación de Instructores",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    create_db_and_tables()


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente"
    }