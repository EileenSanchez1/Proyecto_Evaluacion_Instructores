"""
Script para migrar fotos de instructores de la carpeta vieja
(backend/uploads/) a la carpeta correcta (backend/app/uploads/).

Ejecutar UNA SOLA VEZ después de aplicar las correcciones:
    python migrar_fotos.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_VIEJA = os.path.join(BASE_DIR, "uploads")
CARPETA_NUEVA = os.path.join(BASE_DIR, "app", "uploads")


def migrar():
    if not os.path.exists(CARPETA_VIEJA):
        print("No existe carpeta vieja (backend/uploads/). Nada que migrar.")
        return

    os.makedirs(CARPETA_NUEVA, exist_ok=True)

    archivos = os.listdir(CARPETA_VIEJA)
    if not archivos:
        print("La carpeta vieja está vacía. Nada que migrar.")
        return

    movidos = 0
    for archivo in archivos:
        origen = os.path.join(CARPETA_VIEJA, archivo)
        destino = os.path.join(CARPETA_NUEVA, archivo)
        if os.path.isfile(origen):
            shutil.move(origen, destino)
            movidos += 1
            print(f"Movido: {archivo}")

    print(f"\nMigración completada. {movidos} archivo(s) movido(s).")
    print(f"Destino: {CARPETA_NUEVA}")


if __name__ == "__main__":
    migrar()
