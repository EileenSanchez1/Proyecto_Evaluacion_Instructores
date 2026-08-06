from fastapi import FastAPI

from app.config.database import create_db_and_tables

app = FastAPI(
    title="API - Sistema de Evaluación de Instructores",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a la API de Evaluación de Instructores"
    }