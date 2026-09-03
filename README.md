# Sistema de Evaluación de Instructores

Sistema web para la evaluación de instructores del SENA, desarrollado con **FastAPI** (Backend), **React + Vite** (Frontend) y **PostgreSQL** (Base de Datos).

Permite a los aprendices evaluar a sus instructores mediante encuestas estructuradas, gestionar fichas de formación, instructores, competencias y generar reportes de evaluación.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu equipo:

| Software | Versión recomendada | Descarga |
| --- | --- | --- |
| **Python** | 3.10 o superior | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18.0 o superior | [nodejs.org](https://nodejs.org/) |
| **PostgreSQL** | 15 o superior | [postgresql.org](https://www.postgresql.org/download/) |
| **Git** | Última versión | [git-scm.com](https://git-scm.com/downloads) |

---

## 📁 Estructura del Proyecto

```text
Proyecto_Evaluacion_Instructores/
├── backend/                  ← Servidor FastAPI
│   ├── main.py               ← Punto de entrada de la aplicación
│   ├── database.py           ← Configuración de la base de datos
│   ├── requirements.txt      ← Dependencias de Python
│   ├── .env                  ← Variables de entorno (crear manualmente)
│   ├── app/                  ← Estructura del backend (routers, models, schemas)
│   └── venv/                 ← Entorno virtual
├── frontend/                 ← Interfaz de usuario en React (Vite)
│   ├── src/                  ← Componentes y vistas
│   ├── package.json          ← Dependencias de Node.js / React
│   └── node_modules/         
├── documentacion/            ← Diagramas y documentación técnica
└── README.md                 ← Este archivo

```

---

## 🚀 Instalación y Configuración Inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/EileenSanchez1/Proyecto_Evaluacion_Instructores.git
cd Proyecto_Evaluacion_Instructores

```

---

### 2. Configurar el Backend (Python / FastAPI)

1. **Entra a la carpeta backend:**
```bash
cd backend

```


2. **Crear y activar el entorno virtual:**
* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate

```


* **Windows (Git Bash):**
```bash
source venv/Scripts/activate

```




3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
pip install python-multipart python-dotenv

```


4. **Crear el archivo `.env`:**
Crea un archivo llamado `.env` dentro de la carpeta `backend` (al mismo nivel que `main.py`) con el siguiente contenido:
```env
DATABASE_URL=postgresql+psycopg2://postgres:CONTRASEÑA@localhost:5432/evaluacion_instructores

```


> ⚠️ **Reemplaza `CONTRASEÑA**` por la clave real de tu usuario `postgres` en PostgreSQL.



---

### 3. Configurar el Frontend (React + Vite)

Abre la carpeta `frontend` e instala los paquetes necesarios:

```bash
cd ../frontend
npm install

```

---

## 🖥️ Ejecución del Proyecto (3 Terminales)

Para ejecutar el sistema completo se requieren **3 terminales o consolas independientes**:

---

### 🖥️ CONSOLA 1 — Base de Datos (PostgreSQL)

Verifica que el servicio de PostgreSQL esté iniciado:

```powershell
# En PowerShell
net start postgresql-x64-17

```

*(Opcional)* Puedes conectarte para crear o verificar la base de datos `evaluacion_instructores`:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres

```

```sql
CREATE DATABASE evaluacion_instructores;
\c evaluacion_instructores
\dt
\q

```

---

### 🖥️ CONSOLA 2 — Backend (FastAPI)

1. Ve a la carpeta backend y activa el entorno virtual:
```powershell
cd C:\Proyecto_Evaluacion_Instructores\backend
.\venv\Scripts\Activate

```


2. Inicia el servidor del backend:
```powershell
uvicorn main:app --reload

```


3. El servidor iniciará en: `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
4. La documentación de la API estará disponible en: `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

---

### 🖥️ CONSOLA 3 — Frontend (React)

1. Ve a la carpeta frontend:
```powershell
cd C:\Proyecto_Evaluacion_Instructores\frontend

```


2. Inicia el servidor de desarrollo de React:
```powershell
npm run dev

```


3. La interfaz web abrirá normalmente en: `http://localhost:5173` (o el puerto indicado por Vite).

---

## 🔑 Paso Obligatorio Inicial: Crear la primera Ficha

> ⚠️ **IMPORTANTE:** Para que un **Aprendiz** pueda registrarse desde la interfaz de React, **debe existir al menos una Ficha registrada previamente en el sistema**.

Para crear la primera Ficha, realiza los siguientes pasos desde la API en Swagger (`[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`):

1. **Obtener Token de Administrador:**
* Abre el endpoint `POST /login/`.
* Ingresa las credenciales por defecto del sistema:
* **Correo:** `admin@evaluacion.com`
* **Contraseña:** `Admin12345`


* Haz clic en **Execute** y copia el texto del `access_token` generado en la respuesta.


2. **Autorizar el Token en Swagger:**
* Ve a la parte superior derecha de la página `/docs` y haz clic en el botón verde **Authorize**.
* Pega el `access_token` en el campo **Value:** (sin la palabra `Bearer`).
* Haz clic en **Authorize** y luego en **Close**.


3. **Crear la Ficha:**
* Despliega el endpoint **`POST /fichas/`**.
* Haz clic en **Try it out** y envía los datos de la nueva ficha (ej. número de ficha y programa de formación).
* Haz clic en **Execute**.



¡Listo! Una vez creada la ficha desde la API, ya puedes ir a la **interfaz web de React**, registrar un nuevo Aprendiz seleccionando dicha ficha e iniciar sesión normalmente.

---

## 📊 Orden recomendado de ejecución

```text
1. Iniciar servicio de PostgreSQL
        ↓
2. Ejecutar FastAPI en la Consola Backend (uvicorn main:app --reload)
        ↓
3. Ejecutar React en la Consola Frontend (npm run dev)
        ↓
4. Abrir Swagger (http://127.0.0.1:8000/docs)
        ↓
5. Hacer login como admin@evaluacion.com y autorizar el Token en Swagger
        ↓
6. Crear una Ficha mediante el endpoint POST /fichas/
        ↓
7. Ir a la interfaz web de React y Registrar un Aprendiz asociado a la Ficha creada
        ↓
8. Iniciar sesión en la interfaz web con la cuenta del Aprendiz

```

---

## 🛠️ Solución de Problemas (Troubleshooting)

| Problema | Causa probable | Solución |
| --- | --- | --- |
| `RuntimeError: Form data requires python-multipart` | Falta la librería para procesar formularios | Ejecutar `pip install python-multipart` |
| `Token '-U' inesperado` | Error de sintaxis en PowerShell al llamar `psql` | Usar el operador `&`: `& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres` |
| `401 Unauthorized` al crear Fichas | No se ha enviado o autorizado el token de acceso | Iniciar sesión en `POST /login/`, copiar el token y pegarlo en el botón **Authorize** de Swagger |
| Error al registrar Aprendiz en la Web | No existe ninguna ficha creada en la base de datos | Crear primero una Ficha desde Swagger (`POST /fichas/`) |
| `Connection refused` | El servicio de PostgreSQL está detenido | Iniciar con `net start postgresql-x64-17` |

---

## 🛠️ Tecnologías utilizadas

* **Backend:** Python, FastAPI, SQLModel, SQLAlchemy, Uvicorn, Python-dotenv, Python-multipart.
* **Frontend:** React, Vite, Node.js.
* **Base de Datos:** PostgreSQL (o SQLite para pruebas persitentes).