# Sistema de Evaluación de Instructores

## Requisitos

Para ejecutar el proyecto se necesita tener instalado:

- Python
- PostgreSQL
- Git

Para comprobar si ya están instalados:

```bash
python --version
````

```bash
git --version
```

```bash
psql --version
```

Si alguno ya está instalado, no es necesario instalarlo nuevamente.

---

# 1. Clonar el proyecto

Abrir Git Bash y ubicarse en la carpeta donde se guardará el proyecto.

```bash
git clone URL_DEL_REPOSITORIO
```

Entrar al proyecto:

```bash
cd Proyecto_Evaluacion_Instructores
```

Entrar al backend:

```bash
cd backend
```

---

# 2. Crear el entorno virtual

Dentro de `backend` ejecutar:

```bash
python -m venv venv
```

Activar el entorno virtual.

En Git Bash:

```bash
source venv/Scripts/activate
```

En CMD:

```cmd
venv\Scripts\activate
```

Debe aparecer:

```text
(venv)
```

al inicio de la consola.

---

# 3. Instalar las dependencias

Con el entorno virtual activo:

```bash
pip install -r requirements.txt
```

Si las dependencias ya están instaladas, no es necesario instalarlas nuevamente.

Para comprobarlas:

```bash
pip list
```

---

# 4. PostgreSQL

PostgreSQL debe estar instalado y ejecutándose.

Comprobar:

```bash
psql --version
```

Si `psql` no aparece como comando, se puede utilizar la ruta de instalación de PostgreSQL.

Por ejemplo:

```cmd
"C:\Program Files\PostgreSQL\17\bin\psql.exe" --version
```

También se puede comprobar que el servicio esté funcionando:

```cmd
sc query postgresql-x64-17
```

Debe aparecer:

```text
ESTADO : 4 RUNNING
```

> El número de versión puede cambiar dependiendo de la instalación.

---

# 5. Crear la base de datos

Abrir PostgreSQL:

```cmd
psql -U postgres
```

Si `psql` no está configurado en el PATH:

```cmd
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

Ingresar la contraseña de PostgreSQL.

Debe aparecer:

```text
postgres=#
```

Crear la base de datos:

```sql
CREATE DATABASE evaluacion_instructores;
```

Después ingresar a ella:

```sql
\c evaluacion_instructores
```

Debe aparecer:

```text
evaluacion_instructores=#
```

Las tablas del proyecto se crean automáticamente cuando se inicia la API.

---

# 6. EJECUCIÓN DEL PROYECTO

Para trabajar correctamente se utilizan tres consolas.

---

## CONSOLA 1 - PostgreSQL

Abrir la primera consola y ejecutar:

```cmd
psql -U postgres
```

Entrar a la base de datos:

```sql
\c evaluacion_instructores
```

Esta consola se mantiene abierta mientras se trabaja con el proyecto.

---

## CONSOLA 2 - API

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

Si todo funciona correctamente aparecerá:

```text
Uvicorn running on http://127.0.0.1:8000
```

No cerrar esta consola.

---

## CONSOLA 3 - Git / comandos

Abrir una tercera consola.

Entrar al backend:

```bash
cd Proyecto_Evaluacion_Instructores/backend
```

Activar el entorno virtual:

```bash
source venv/Scripts/activate
```

Esta consola se utiliza para ejecutar comandos adicionales sin detener la API.

Por ejemplo:

```bash
git status
```

Para actualizar los cambios del repositorio:

```bash
git pull
```

---

# 7. Comprobar que la API funciona

Abrir el navegador:

```text
http://127.0.0.1:8000
```

Debe aparecer:

```json
{
    "mensaje": "API funcionando correctamente"
}
```

También se puede abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

Desde Swagger se pueden realizar las pruebas del proyecto.

---

# 8. CREAR UNA FICHA

Para poder iniciar sesión primero debe existir una ficha.

En Swagger:

```text
http://127.0.0.1:8000/docs
```

Buscar:

```text
Fichas
```

Seleccionar:

```text
POST /fichas/
```

Presionar:

```text
Try it out
```

Ingresar los datos solicitados por `FichaCreate`.

Ejecutar con:

```text
Execute
```

La ficha quedará almacenada en PostgreSQL.

---

# 9. CREAR EL APRENDIZ

Después de crear la ficha se debe crear un aprendiz asociado a esa ficha.

En Swagger buscar:

```text
Aprendices
```

Seleccionar:

```text
POST /aprendices/
```

Presionar:

```text
Try it out
```

Ingresar los datos solicitados por `AprendizCreate`.

El aprendiz debe tener:

* Sus datos personales
* Correo
* Contraseña
* La ficha correspondiente

Ejecutar con:

```text
Execute
```

El aprendiz quedará guardado en PostgreSQL.

---

# 10. PROBAR EL LOGIN

Una vez creada la ficha y el aprendiz:

En Swagger buscar:

```text
Login
```

Seleccionar:

```text
POST /login/
```

Presionar:

```text
Try it out
```

Ingresar el mismo correo y contraseña utilizados al crear el aprendiz.

Ejemplo:

```json
{
    "correo": "correo@ejemplo.com",
    "contrasena": "123456"
}
```

Presionar:

```text
Execute
```

Si los datos son correctos, el login será exitoso y se mostrará la información del aprendiz.

---

# 11. Orden para ejecutar el proyecto

El orden correcto es:

```text
1. Instalar Python, PostgreSQL y Git
            ↓
2. Clonar el repositorio
            ↓
3. Crear el entorno virtual
            ↓
4. Activar el entorno virtual
            ↓
5. Instalar requirements.txt
            ↓
6. Crear la base de datos
   evaluacion_instructores
            ↓
7. Abrir las 3 consolas
            ↓
8. Iniciar PostgreSQL
            ↓
9. Ejecutar FastAPI
            ↓
10. Abrir Swagger
            ↓
11. Crear una Ficha
            ↓
12. Crear un Aprendiz asociado a la Ficha
            ↓
13. Realizar Login
```

## Importante

No es necesario crear manualmente las tablas de PostgreSQL.

La aplicación las crea automáticamente al iniciar FastAPI mediante:

```python
create_db_and_tables()
```

La base de datos que debe existir previamente es:

```text
evaluacion_instructores
```

```

**Así sí queda limpio:** instalación → PostgreSQL → 3 consolas → API → crear ficha → crear aprendiz → login. Nada de meter Instructores, Ficha-Instructor, Reportes, etc.
```
