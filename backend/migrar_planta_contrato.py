"""
Agrega la columna planta_contrato a la tabla instructores si no existe.
Ejecutar una vez desde la carpeta backend:

  python migrar_planta_contrato.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from app.config.database import engine  # noqa: E402


def main():
    with engine.connect() as conn:
        dialect = engine.dialect.name
        if dialect == "sqlite":
            cols = conn.execute(text("PRAGMA table_info(instructores)")).fetchall()
            nombres = {c[1] for c in cols}
            if "planta_contrato" not in nombres:
                conn.execute(
                    text(
                        "ALTER TABLE instructores ADD COLUMN planta_contrato VARCHAR(20)"
                    )
                )
                conn.commit()
                print("OK: columna planta_contrato agregada (SQLite).")
            else:
                print("OK: columna planta_contrato ya existe.")
        else:
            # PostgreSQL
            exists = conn.execute(
                text(
                    """
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'instructores' AND column_name = 'planta_contrato'
                    """
                )
            ).fetchone()
            if not exists:
                conn.execute(
                    text(
                        "ALTER TABLE instructores ADD COLUMN planta_contrato VARCHAR(20)"
                    )
                )
                conn.commit()
                print("OK: columna planta_contrato agregada (PostgreSQL).")
            else:
                print("OK: columna planta_contrato ya existe.")


if __name__ == "__main__":
    main()
