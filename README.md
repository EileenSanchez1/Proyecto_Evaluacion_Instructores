# Sistema de Evaluación de Instructores

## Ejecución del proyecto

Sigue estos pasos en orden para ejecutar el proyecto correctamente.

---

## 1. Clonar el repositorio

Desde una consola:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_Evaluacion_Instructores/backend

Si el repositorio ya está clonado, entra directamente a la carpeta backend.

## 2. Crear y activar el entorno virtual

En Windows:

python -m venv venv
Activar en Git Bash
source venv/Scripts/activate
Activar en CMD
venv\Scripts\activate

Cuando esté activado debe aparecer:

(venv)

al inicio de la consola.

## 3. Instalar las dependencias

Con el entorno virtual activado:

pip install -r requirements.txt
Si las dependencias ya están instaladas

No es necesario volver a instalarlas.

Se pueden comprobar con:

pip list

Si falta alguna dependencia:

pip install -r requirements.txt
## 4. Configurar el archivo .env

NO OLVIDAR EL ARCHIVO .env.

El archivo .env debe estar dentro de la carpeta backend, al mismo nivel que main.py.

El archivo contiene la configuración necesaria para conectarse a PostgreSQL.

Ejemplo:

DATABASE_URL=postgresql+psycopg2://postgres:CONTRASEÑA@localhost:5432/evaluacion_instructores

Se debe reemplazar CONTRASEÑA por la contraseña configurada para el usuario de PostgreSQL.

Importante

El archivo .env es necesario para que la aplicación pueda conectarse correctamente a la base de datos.

Ejecución con 3 consolas

Para ejecutar el proyecto se recomienda utilizar 3 consolas.

CONSOLA 1 — PostgreSQL

Primero se debe verificar que PostgreSQL esté funcionando.

Desde CMD:

sc query postgresql-x64-17

Debe aparecer:

ESTADO : 4  RUNNING

Si el servicio está detenido:

net start postgresql-x64-17

Después se puede entrar a PostgreSQL con:

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres

Ingresar la contraseña de PostgreSQL que cada quien tenga en su dispositivo.

Entrar a la base de datos del proyecto:

\c evaluacion_instructores

Comprobar la base de datos:

SELECT current_database();

Para ver las tablas:

\dt

Para salir de PostgreSQL:

\q
CONSOLA 2 — Backend / FastAPI

Abrir una segunda consola.

Entrar a la carpeta del backend:

cd Proyecto_Evaluacion_Instructores/backend

Activar el entorno virtual:

source venv/Scripts/activate

Ejecutar FastAPI:

uvicorn main:app --reload

Si todo funciona correctamente aparecerá algo parecido a:

Uvicorn running on http://127.0.0.1:8000

La documentación de la API estará disponible en:

http://127.0.0.1:8000/docs
CONSOLA 3 — Verificar la base de datos

Abrir una tercera consola.

Entrar a PostgreSQL:

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres

Entrar a la base de datos:

\c evaluacion_instructores

Ver las tablas:

\dt

Las tablas se crean automáticamente al iniciar la API mediante:

create_db_and_tables()
## 5. Crear una Ficha

Antes de iniciar sesión debe existir una Ficha.

Abrir Swagger:

http://127.0.0.1:8000/docs

Buscar:

Fichas → POST /fichas/

Crear una ficha utilizando los campos solicitados por FichaCreate.

Por ejemplo, si el esquema utiliza un número de ficha:

{
  "numero_ficha": 2876543
}

Los campos exactos dependen del esquema actual del proyecto.

Después se puede comprobar con:

Fichas → GET /fichas/

## 6. Crear un Aprendiz

También debe existir un Aprendiz asociado a una Ficha para poder iniciar sesión.

En Swagger:

Aprendices → POST /aprendices/

Crear el aprendiz utilizando los campos solicitados por AprendizCreate.

Por ejemplo:

{
  "nombre": "Eileen",
  "apellido": "Sanchez",
  "correo": "eileen@gmail.com",
  "contrasena": "123456",
  "id_ficha": 1
}

Los campos exactos deben coincidir con el AprendizCreate actual del proyecto.

Después se puede comprobar con:

Aprendices → GET /aprendices/

## 7. Iniciar sesión

Cuando ya exista:

La base de datos.
Una Ficha.
Un Aprendiz asociado a esa Ficha.
El correo y contraseña del Aprendiz.

Se puede utilizar:

Login → POST /login/

Ejemplo:

{
  "correo": "eileen@gmail.com",
  "contrasena": "123456"
}

Si los datos son correctos, la API devolverá el mensaje de inicio de sesión y la información del aprendiz.

Orden recomendado
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
Comandos principales
Crear entorno virtual
python -m venv venv
Activar entorno virtual en Git Bash
source venv/Scripts/activate
Instalar dependencias
pip install -r requirements.txt
Ejecutar FastAPI
uvicorn main:app --reload
Iniciar PostgreSQL
net start postgresql-x64-17
Entrar a PostgreSQL
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
Entrar a la base de datos
\c evaluacion_instructores
Ver tablas
\dt
Swagger

Con FastAPI ejecutándose:

http://127.0.0.1:8000/docs

Desde Swagger se pueden probar los endpoints de la API.

Importante
Verificar que PostgreSQL esté iniciado antes de ejecutar la API.
Verificar que exista la base de datos evaluacion_instructores.
No olvidar el archivo .env.
El .env debe estar dentro de backend.
Activar el entorno virtual antes de ejecutar FastAPI.
Si las dependencias ya están instaladas, no es necesario instalarlas nuevamente.
Crear primero la Ficha.
Después crear el Aprendiz asociado a esa Ficha.
Para iniciar sesión se utiliza el correo y contraseña del Aprendiz creado.
