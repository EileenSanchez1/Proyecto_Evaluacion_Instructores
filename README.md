[README.md](https://github.com/user-attachments/files/31720214/README.md)
# Sistema de Evaluación de Instructores

Sistema web para la evaluación de instructores del SENA, desarrollado con **FastAPI** y **PostgreSQL**.

Permite a los aprendices evaluar a sus instructores mediante encuestas estructuradas, gestionar fichas de formación, instructores, competencias y generar reportes de evaluación.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu equipo:

| Software | Versión recomendada | Descarga |
|----------|---------------------|----------|
| Python | 3.10 o superior | [python.org](https://www.python.org/downloads/) |
| PostgreSQL | 15 o superior | [postgresql.org](https://www.postgresql.org/download/) |
| Git | Última versión | [git-scm.com](https://git-scm.com/downloads) |
| Visual Studio Code (opcional) | Última versión | [code.visualstudio.com](https://code.visualstudio.com/) |

> **Nota:** Este proyecto está configurado para ejecutarse en **Windows** con Git Bash o CMD.

---

## 📁 Estructura del Proyecto

```
Proyecto_Evaluacion_Instructores/
├── backend/
│   ├── main.py              ← Punto de entrada de la aplicación
│   ├── database.py          ← Configuración de la base de datos
│   ├── requirements.txt     ← Dependencias de Python
│   ├── .env                 ← Variables de entorno (crear manualmente)
│   ├── models/              ← Modelos SQLModel
│   ├── routers/             ← Endpoints de la API
│   ├── schemas/             ← Esquemas Pydantic
│   └── services/            ← Lógica de negocio
├── documentacion/           ← Diagramas y documentación técnica
├── README.md                ← Este archivo
└── .gitignore
```

---

## 🚀 Instalación y Configuración

Sigue estos pasos en **orden** para ejecutar el proyecto correctamente.

---

### 1. Clonar el repositorio

Desde una consola (Git Bash o CMD):

```bash
git clone https://github.com/EileenSanchez1/Proyecto_Evaluacion_Instructores.git
cd Proyecto_Evaluacion_Instructores/backend
```

Si el repositorio ya está clonado, entra directamente a la carpeta `backend`.

---

### 2. Crear y activar el entorno virtual

#### Windows

Crear el entorno virtual:

```bash
python -m venv venv
```

**Git Bash:**

```bash
source venv/Scripts/activate
```

**CMD:**

```cmd
venv\Scripts\activate
```

Cuando el entorno esté activado debe aparecer:

```text
(venv)
```

al inicio de la consola.

---

### 3. Instalar las dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Si las dependencias ya están instaladas, **no es necesario volver a instalarlas**.

Para comprobar las dependencias instaladas:

```bash
pip list
```

Si falta alguna dependencia:

```bash
pip install -r requirements.txt
```

---

### 4. Configurar el archivo `.env`

> **⚠️ IMPORTANTE: NO OLVIDAR EL ARCHIVO `.env`.**

El archivo `.env` debe estar dentro de la carpeta `backend`, al mismo nivel que `main.py`.

Ejemplo:

```env
DATABASE_URL=postgresql+psycopg2://postgres:CONTRASEÑA@localhost:5432/evaluacion_instructores
```

Se debe reemplazar `CONTRASEÑA` por la contraseña configurada para el usuario de PostgreSQL en tu equipo.

El archivo `.env` es necesario para que la aplicación pueda conectarse correctamente a la base de datos.

---

## 🖥️ Ejecución del Proyecto

Se recomienda utilizar **3 consolas** para ejecutar y verificar el proyecto.

---

## 🖥️ CONSOLA 1 — PostgreSQL

Primero se debe verificar que PostgreSQL esté funcionando.

Desde CMD:

```cmd
sc query postgresql-x64-17
```

Debe aparecer un estado similar a:

```text
ESTADO : 4  RUNNING
```

Si el servicio está detenido:

```cmd
net start postgresql-x64-17
```

### Entrar a PostgreSQL

```cmd
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

Ingresar la contraseña de PostgreSQL configurada en el equipo.

### Entrar a la base de datos

```sql
\c evaluacion_instructores
```

Comprobar la base de datos actual:

```sql
SELECT current_database();
```

Para ver las tablas:

```sql
\dt
```

Para salir de PostgreSQL:

```sql
\q
```

---

## 🖥️ CONSOLA 2 — Backend / FastAPI

Abrir una segunda consola.

Entrar a la carpeta del backend:

```bash
cd Proyecto_Evaluacion_Instructores/backend
```

Activar el entorno virtual:

```bash
source venv/Scripts/activate
```

Ejecutar FastAPI:

```bash
uvicorn main:app --reload
```

Si todo funciona correctamente aparecerá algo similar a:

```text
Uvicorn running on http://127.0.0.1:8000
```

### Documentación de la API

La documentación de Swagger estará disponible en:

```text
http://127.0.0.1:8000/docs
```

---

## 🖥️ CONSOLA 3 — Verificar la base de datos

Abrir una tercera consola.

Entrar a PostgreSQL:

```cmd
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

Entrar a la base de datos:

```sql
\c evaluacion_instructores
```

Ver las tablas:

```sql
\dt
```

Las tablas se crean automáticamente al iniciar la API mediante:

```python
create_db_and_tables()
```



## Iniciar sesión

Cuando ya existan:

* La base de datos.
* El registro activo
* Orden seguido de ejecucion ya dicho previamente
* El correo y contraseña del Aprendiz.

Se puede realizar el inicio de sesión desde:



Si los datos son correctos, se devolverá el mensaje de inicio de sesión y la información correspondiente del aprendiz.

---

## 📊 Orden recomendado de ejecución

```text
1. Iniciar PostgreSQL
        ↓
2. Verificar la base de datos evaluacion_instructores
        ↓
3. Verificar el archivo .env
        ↓
4. Activar el entorno virtual
        ↓
5. Instalar requirements.txt si hace falta
        ↓
6. Ejecutar FastAPI
        ↓
7. Abrir Swagger /docs
        ↓
8. Abrir el localhost de react
        ↓
9. Registrarse como aprendiz
        ↓
10. Iniciar sesión
```

---

## 📋 Comandos principales

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual — Git Bash

```bash
source venv/Scripts/activate
```

### Activar entorno virtual — CMD

```cmd
venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar FastAPI

```bash
uvicorn main:app --reload
```

### Iniciar PostgreSQL

```cmd
net start postgresql-x64-17
```

### Entrar a PostgreSQL

```cmd
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

### Entrar a la base de datos

```sql
\c evaluacion_instructores
```

### Ver tablas

```sql
\dt
```

---

## 🔍 Documentación de la API (Swagger)

Con FastAPI ejecutándose, acceder a:

```text
http://127.0.0.1:8000/docs
```

Desde Swagger se pueden consultar y probar los diferentes endpoints de la API de forma interactiva.

También está disponible la documentación alternativa en:

```text
http://127.0.0.1:8000/redoc
```

---

## ⚠️ Importante

Antes de ejecutar el proyecto, verificar lo siguiente:

* PostgreSQL debe estar iniciado.
* Debe existir la base de datos `evaluacion_instructores`.
* Debe existir el archivo `.env`.
* El archivo `.env` debe estar dentro de `backend`.
* La contraseña de PostgreSQL del `.env` debe ser correcta.
* El entorno virtual debe estar activado en backend antes de ejecutar FastAPI.
* Si las dependencias ya están instaladas, no es necesario instalarlas nuevamente.
* Primero se debe crear la **Ficha**.
* Después se debe crear el **Aprendiz asociado a esa Ficha**.
* Para iniciar sesión se utiliza el correo y contraseña del Aprendiz creado.

---

## 🛠️ Solución de Problemas (Troubleshooting)

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| `ModuleNotFoundError` | Dependencias no instaladas | Ejecutar `pip install -r requirements.txt` con el entorno virtual activado |
| `Connection refused` | PostgreSQL no está corriendo | Verificar con `sc query postgresql-x64-17` e iniciar con `net start postgresql-x64-17` |
| Error de autenticación en login | Datos incorrectos o Aprendiz no creado | Verificar que el Aprendiz exista en la base de datos y que el correo y contraseña sean correctos |
| No se crean las tablas | Error en la conexión a la base de datos | Revisar que el archivo `.env` tenga la URL correcta y que PostgreSQL esté activo |
| Puerto 8000 en uso | Otra aplicación está usando el puerto | Cambiar el puerto con `uvicorn main:app --reload --port 8001` |

---

## 📚 Endpoints principales

| Módulo | Descripción |
|--------|-------------|
| **Fichas** | Gestión de fichas de formación |
| **Aprendices** | Registro y gestión de aprendices |
| **Instructores** | Gestión de instructores |
| **Competencias** | Administración de competencias |
| **Encuestas** | Creación y gestión de encuestas de evaluación |
| **Login** | Autenticación de usuarios |

---

## 🛠️ Tecnologías utilizadas

* **Python** — Lenguaje de programación
* **FastAPI** — Framework web de alto rendimiento
* **SQLModel** — ORM para modelos SQL
* **PostgreSQL** — Sistema de gestión de bases de datos relacional
* **Pydantic** — Validación de datos y serialización
* **Uvicorn** — Servidor ASGI para ejecutar la aplicación
* **psycopg2** — Driver de PostgreSQL para Python
* **python-dotenv** — Gestión de variables de entorno

---

> 📌 **Estado del proyecto:** Finalizado parcial — Listo para pruebas.
