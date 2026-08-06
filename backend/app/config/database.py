from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Leer variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Cadena de conexión a PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Función para obtener una sesión
def get_session():
    with Session(engine) as session:
        yield session


# Función para crear las tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)