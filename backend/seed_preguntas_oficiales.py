"""
Carga las 19 preguntas del formato oficial SENA (evaluación instructores en aula).

Uso (desde carpeta backend, con venv activo y DB configurada):
  python seed_preguntas_oficiales.py
  python seed_preguntas_oficiales.py --reemplazar
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlmodel import Session, select
from app.config.database import engine
from app.models.pregunta import Pregunta
import json


def main(reemplazar: bool = False):
    data_path = Path(__file__).resolve().parent / "app" / "data" / "preguntas_oficiales_sena.json"
    with open(data_path, encoding="utf-8") as f:
        oficiales = json.load(f)

    with Session(engine) as session:
        if reemplazar:
            for p in session.exec(select(Pregunta)).all():
                p.estado = False
                session.add(p)
            session.commit()

        creadas = omitidas = 0
        for item in oficiales:
            desc = item["descripcion"].strip()
            orden = int(item["orden"])
            ya = session.exec(select(Pregunta).where(Pregunta.descripcion == desc)).first()
            if ya:
                if reemplazar:
                    ya.estado = True
                    ya.orden = orden
                    session.add(ya)
                omitidas += 1
                continue
            session.add(Pregunta(descripcion=desc, orden=orden, estado=True))
            creadas += 1
        session.commit()
        print(f"OK: {creadas} creadas, {omitidas} omitidas/actualizadas. Total oficiales: {len(oficiales)}")


if __name__ == "__main__":
    main(reemplazar="--reemplazar" in sys.argv)
