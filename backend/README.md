# Sistema de Evaluación de Instructores

API REST desarrollada con **FastAPI**, **SQLModel** y **PostgreSQL** para gestionar la evaluación de instructores del SENA.

---

# Tecnologías utilizadas

- Python 3.12+
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- Psycopg2
- Uvicorn
- Python Dotenv

---

# Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd nombre-del-proyecto
```

---

# Crear el entorno virtual

### Windows

```bash
python -m venv .venv
```

### Linux / macOS

```bash
python3 -m venv .venv
```

---

# Activar el entorno virtual

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### Windows (CMD)

```cmd
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Cuando el entorno esté activo aparecerá algo similar a:

```text
(.venv)
```

al inicio de la terminal.

---

# Instalar dependencias

> **Importante:** Antes de instalar las dependencias, asegúrate de haber creado y activado el entorno virtual.

## Si el proyecto YA incluye el archivo `requirements.txt`

Ejecuta:

```bash
pip install -r requirements.txt
```

Este comando instalará automáticamente todas las dependencias necesarias.

---

## Si el proyecto NO incluye el archivo `requirements.txt`

Instala las dependencias manualmente:

```bash
pip install fastapi
pip install uvicorn
pip install sqlmodel
pip install sqlalchemy
pip install psycopg2-binary
pip install python-dotenv
```

Luego genera el archivo `requirements.txt` para futuras instalaciones:

```bash
pip freeze > requirements.txt
```

---

# Configurar PostgreSQL

Crear una base de datos en PostgreSQL.

Ejemplo:

```
evaluacion_instructores
```

---

# Configurar variables de entorno

Crear un archivo llamado:

```
.env
```

En la raíz del proyecto.

Ejemplo:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=evaluacion_instructores
DB_USER=postgres
DB_PASSWORD=tu_contraseña (la que cada quien registro en el postgres del computador en el que se va a trabajar , ES NECESARIO PARA EJECUTAR)
```

> **Importante:** El archivo `.env` es personal para cada integrante del equipo y **no debe subirse al repositorio**.

---

# Ejecutar la aplicación

Una vez configurado el entorno y la base de datos, ejecutar:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```
http://127.0.0.1:8000
```

---

# Documentación de la API

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Creación automática de tablas

Al iniciar la aplicación por primera vez, FastAPI ejecuta automáticamente:

```python
SQLModel.metadata.create_all(engine)
```

Esto crea todas las tablas definidas en los modelos si aún no existen.

No es necesario ejecutar scripts SQL manualmente.

---

# Estructura del proyecto

```
app/
│
├── config/
│   └── database.py
│
├── models/
│   ├── __init__.py
│   ├── aprendiz.py
│   ├── evaluacion.py
│   ├── ficha.py
│   ├── ficha_instructor.py
│   ├── instructor.py
│   ├── pregunta.py
│   └── respuesta.py
│
├── schemas/
│   ├── aprendiz.py
│   ├── evaluacion.py
│   ├── ficha.py
│   ├── ficha_instructor.py
│   ├── instructor.py
│   ├── pregunta.py
│   └── respuesta.py
│
├── main.py
│
└── ...
```

---

# Modelos implementados

- Ficha
- Aprendiz
- Instructor
- Pregunta
- Evaluación
- Respuesta
- FichaInstructor

---

# Relaciones del sistema

- Ficha → Aprendices
- Ficha → FichaInstructor
- Instructor → FichaInstructor
- Aprendiz → Evaluación
- Evaluación → Respuesta
- Respuesta → Pregunta
- Respuesta → Instructor

---

# Recomendaciones para el equipo

Antes de comenzar a trabajar:

1. Hacer `git pull` para obtener los últimos cambios.
2. Activar el entorno virtual.
3. Instalar las dependencias.
4. Verificar que el archivo `.env` esté correctamente configurado.
5. Ejecutar la aplicación.
6. Trabajar siempre en una rama propia antes de realizar un Pull Request.

---

# Importante

- No modificar `database.py` sin informar al equipo.
- No cambiar los nombres de las tablas ni de las claves primarias.
- No modificar las relaciones (`Relationship` y `back_populates`) sin revisar el impacto en el proyecto.
- Si se agrega un nuevo modelo, importarlo en `app/models/__init__.py` para que SQLModel pueda crear la tabla automáticamente.
- No subir el archivo `.env` al repositorio.
- No subir el entorno virtual (`.venv`).
-No realizar cambios en lo que esta hecho solo en lo que le corresponde  a cada uno

---

# Estado actual del proyecto

- PostgreSQL configurado
- Conexión a la base de datos
- Modelos implementados
- Schemas implementados
- Relaciones configuradas
- Creación automática de tablas
- Base lista para desarrollar Repositories, Services y Routers