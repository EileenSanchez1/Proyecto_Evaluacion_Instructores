"""
Agrega la columna 'activo' a ficha_instructor si no existe.
Ejecutar una vez desde la carpeta backend:
  python migrar_ficha_instructor_activo.py
"""
import os
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
if not url:
    # fallback common
    print("Define DATABASE_URL en .env")
    raise SystemExit(1)

engine = create_engine(url)
with engine.begin() as conn:
    # PostgreSQL
    exists = conn.execute(
        text(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'ficha_instructor' AND column_name = 'activo'
            """
        )
    ).scalar()
    if exists:
        print("Columna 'activo' ya existe. Nada que hacer.")
    else:
        conn.execute(
            text(
                "ALTER TABLE ficha_instructor ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE"
            )
        )
        print("Columna 'activo' agregada con DEFAULT TRUE.")
print("Listo.")
