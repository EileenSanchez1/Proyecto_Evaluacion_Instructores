# Sistema de Evaluación de Instructores

Sistema web para la evaluación de instructores, desarrollado con **FastAPI** y **PostgreSQL**.

---

## Ejecución del proyecto

Sigue estos pasos en orden para ejecutar el proyecto correctamente.

### 1. Clonar el repositorio

Desde una consola:

```bash
git clone <URL_DEL_REPOSITORIO>
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

Se debe reemplazar `CONTRASEÑA` por la contraseña configurada para el usuario de PostgreSQL.

El archivo `.env` es necesario para que la aplicación pueda conectarse correctamente a la base de datos.

---

# Ejecución del proyecto

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

---

# Crear los datos necesarios para iniciar sesión

Antes de iniciar sesión debe existir una **Ficha** y un **Aprendiz asociado a esa Ficha**.

---

## 5. Crear una Ficha

Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

Buscar:

```text
Fichas → POST /fichas/
```

Crear una ficha utilizando los campos solicitados por `FichaCreate`.

Por ejemplo:

```json
{
  "numero_ficha": 2876543
}
```

> Los campos exactos dependen del esquema actual del proyecto.

Después se puede comprobar utilizando:

```text
Fichas → GET /fichas/
```

---

## 6. Crear un Aprendiz

También debe existir un **Aprendiz asociado a una Ficha** para poder iniciar sesión.

En Swagger:

```text
Aprendices → POST /aprendices/
```

Crear el aprendiz utilizando los campos solicitados por `AprendizCreate`.

Por ejemplo:

```json
{
  "nombre": "Eileen",
  "apellido": "Sanchez",
  "correo": "eileen@gmail.com",
  "contrasena": "123456",
  "id_ficha": 1
}
```

> Los campos exactos deben coincidir con el `AprendizCreate` actual del proyecto.

Después se puede comprobar utilizando:

```text
Aprendices → GET /aprendices/
```

---

# 7. Iniciar sesión

Cuando ya existan:

* La base de datos.
* Una Ficha.
* Un Aprendiz asociado a esa Ficha.
* El correo y contraseña del Aprendiz.

Se puede realizar el inicio de sesión desde:

```text
Login → POST /login/
```

Ejemplo:

```json
{
  "correo": "eileen@gmail.com",
  "contrasena": "123456"
}
```

Si los datos son correctos, la API devolverá el mensaje de inicio de sesión y la información correspondiente del aprendiz.

---

# Orden recomendado

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
8. Crear una Ficha
        ↓
9. Crear un Aprendiz asociado a la Ficha
        ↓
10. Iniciar sesión
```

---

# Comandos principales

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

# Swagger

Con FastAPI ejecutándose, acceder a:

```text
http://127.0.0.1:8000/docs
```

Desde Swagger se pueden consultar y probar los diferentes endpoints de la API.

---

# ⚠️ Importante

Antes de ejecutar el proyecto, verificar lo siguiente:

* PostgreSQL debe estar iniciado.
* Debe existir la base de datos `evaluacion_instructores`.
* Debe existir el archivo `.env`.
* El archivo `.env` debe estar dentro de `backend`.
* La contraseña de PostgreSQL del `.env` debe ser correcta.
* El entorno virtual debe estar activado antes de ejecutar FastAPI.
* Si las dependencias ya están instaladas, no es necesario instalarlas nuevamente.
* Primero se debe crear la **Ficha**.
* Después se debe crear el **Aprendiz asociado a esa Ficha**.
* Para iniciar sesión se utiliza el correo y contraseña del Aprendiz creado.

---

## Tecnologías utilizadas

* **Python**
* **FastAPI**
* **SQLModel**
* **PostgreSQL**
* **Pydantic**
* **Uvicorn**
* **psycopg2**
* **python-dotenv**
