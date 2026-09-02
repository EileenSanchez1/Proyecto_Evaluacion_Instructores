from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

from app.models import *

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Si todas las variables de PostgreSQL están configuradas, usar PostgreSQL
if all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"options": "-c lc_messages=C"}
    )
    print("✅ Conectado a PostgreSQL")
else:
    # Fallback a SQLite persistente en archivo (los datos NO se borran al cerrar)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SQLITE_PATH = os.path.join(BASE_DIR, "database.sqlite")
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
    print(f"⚠️  Usando SQLite persistente: {SQLITE_PATH}")

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
