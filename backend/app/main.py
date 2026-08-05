from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicialización de la app con Swagger (se habilita automáticamente en /docs)
app = FastAPI(
    title="Proyecto Evaluación Instructores",
    description="API Backend para el sistema de evaluación",
    version="1.0.0",
    docs_url="/docs",      # Ruta para Swagger UI
    redoc_url="/redoc"     # Ruta para ReDoc (opcional)
)

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Cambia o agrega los puertos según tu Frontend
    "http://localhost:5173",  # Puerto por defecto de Vite/React
    "*"                       # Permite todos los orígenes durante desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"mensaje": "Backend de Evaluación de Instructores funcionando correctamente"}