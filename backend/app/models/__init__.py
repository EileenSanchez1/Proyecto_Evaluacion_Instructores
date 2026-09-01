import os
import importlib

# Obtener la ruta de la carpeta actual (models)
models_dir = os.path.dirname(__file__)

# Recorrer todos los archivos de la carpeta
for filename in os.listdir(models_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        # Importar dinámicamente cada módulo de la carpeta models
        importlib.import_module(f".{module_name}", package=__name__)