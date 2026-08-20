from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from typing import List

from app.config.database import create_db_and_tables, get_session

# Repositories
from app.repositories.ficha_repository import FichaRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.aprendiz_repository import AprendizRepository
from app.repositories.pregunta_repository import PreguntaRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.respuesta_repository import RespuestaRepository

# Schemas
from app.schemas.ficha import FichaCreate, FichaUpdate, FichaResponse
from app.schemas.instructor import InstructorCreate, InstructorUpdate, InstructorResponse
from app.schemas.aprendiz import AprendizCreate, AprendizUpdate, AprendizResponse
from app.schemas.pregunta import PreguntaCreate, PreguntaUpdate, PreguntaResponse
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate, EvaluacionResponse
from app.schemas.respuesta import RespuestaCreate, RespuestaUpdate, RespuestaResponse

app = FastAPI(
    title="Sistema de Evaluación de Instructores",
    description="API REST para gestionar la evaluación de instructores del SENA",
    version="1.0.0"
)

# CORS (para conectar con tu frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ============================================================
# FICHAS
# ============================================================
@app.post("/fichas", response_model=FichaResponse, tags=["Fichas"])
def crear_ficha(ficha: FichaCreate, session: Session = Depends(get_session)):
    return FichaRepository.crear(session, ficha)


@app.get("/fichas", response_model=List[FichaResponse], tags=["Fichas"])
def listar_fichas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return FichaRepository.listar(session, offset=offset, limit=limit)


@app.get("/fichas/{ficha_id}", response_model=FichaResponse, tags=["Fichas"])
def buscar_ficha(ficha_id: int, session: Session = Depends(get_session)):
    ficha = FichaRepository.buscar(session, ficha_id)
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return ficha


@app.put("/fichas/{ficha_id}", response_model=FichaResponse, tags=["Fichas"])
def actualizar_ficha(ficha_id: int, ficha_update: FichaUpdate, session: Session = Depends(get_session)):
    ficha = FichaRepository.actualizar(session, ficha_id, ficha_update)
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return ficha


@app.delete("/fichas/{ficha_id}", tags=["Fichas"])
def eliminar_ficha(ficha_id: int, session: Session = Depends(get_session)):
    eliminado = FichaRepository.eliminar(session, ficha_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Ficha no encontrada")
    return {"message": "Ficha eliminada correctamente"}


# ============================================================
# INSTRUCTORES
# ============================================================
@app.post("/instructores", response_model=InstructorResponse, tags=["Instructores"])
def crear_instructor(instructor: InstructorCreate, session: Session = Depends(get_session)):
    return InstructorRepository.crear(session, instructor)


@app.get("/instructores", response_model=List[InstructorResponse], tags=["Instructores"])
def listar_instructores(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return InstructorRepository.listar(session, offset=offset, limit=limit)


@app.get("/instructores/{instructor_id}", response_model=InstructorResponse, tags=["Instructores"])
def buscar_instructor(instructor_id: int, session: Session = Depends(get_session)):
    instructor = InstructorRepository.buscar(session, instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return instructor


@app.put("/instructores/{instructor_id}", response_model=InstructorResponse, tags=["Instructores"])
def actualizar_instructor(instructor_id: int, instructor_update: InstructorUpdate, session: Session = Depends(get_session)):
    instructor = InstructorRepository.actualizar(session, instructor_id, instructor_update)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return instructor


@app.delete("/instructores/{instructor_id}", tags=["Instructores"])
def eliminar_instructor(instructor_id: int, session: Session = Depends(get_session)):
    eliminado = InstructorRepository.eliminar(session, instructor_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return {"message": "Instructor eliminado correctamente"}


# ============================================================
# APRENDICES
# ============================================================
@app.post("/aprendices", response_model=AprendizResponse, tags=["Aprendices"])
def crear_aprendiz(aprendiz: AprendizCreate, session: Session = Depends(get_session)):
    return AprendizRepository.crear(session, aprendiz)


@app.get("/aprendices", response_model=List[AprendizResponse], tags=["Aprendices"])
def listar_aprendices(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return AprendizRepository.listar(session, offset=offset, limit=limit)


@app.get("/aprendices/{aprendiz_id}", response_model=AprendizResponse, tags=["Aprendices"])
def buscar_aprendiz(aprendiz_id: int, session: Session = Depends(get_session)):
    aprendiz = AprendizRepository.buscar(session, aprendiz_id)
    if not aprendiz:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return aprendiz


@app.put("/aprendices/{aprendiz_id}", response_model=AprendizResponse, tags=["Aprendices"])
def actualizar_aprendiz(aprendiz_id: int, aprendiz_update: AprendizUpdate, session: Session = Depends(get_session)):
    aprendiz = AprendizRepository.actualizar(session, aprendiz_id, aprendiz_update)
    if not aprendiz:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return aprendiz


@app.delete("/aprendices/{aprendiz_id}", tags=["Aprendices"])
def eliminar_aprendiz(aprendiz_id: int, session: Session = Depends(get_session)):
    eliminado = AprendizRepository.eliminar(session, aprendiz_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")
    return {"message": "Aprendiz eliminado correctamente"}


# ============================================================
# PREGUNTAS
# ============================================================
@app.post("/preguntas", response_model=PreguntaResponse, tags=["Preguntas"])
def crear_pregunta(pregunta: PreguntaCreate, session: Session = Depends(get_session)):
    return PreguntaRepository.crear(session, pregunta)


@app.get("/preguntas", response_model=List[PreguntaResponse], tags=["Preguntas"])
def listar_preguntas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return PreguntaRepository.listar(session, offset=offset, limit=limit)


@app.get("/preguntas/{pregunta_id}", response_model=PreguntaResponse, tags=["Preguntas"])
def buscar_pregunta(pregunta_id: int, session: Session = Depends(get_session)):
    pregunta = PreguntaRepository.buscar(session, pregunta_id)
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return pregunta


@app.put("/preguntas/{pregunta_id}", response_model=PreguntaResponse, tags=["Preguntas"])
def actualizar_pregunta(pregunta_id: int, pregunta_update: PreguntaUpdate, session: Session = Depends(get_session)):
    pregunta = PreguntaRepository.actualizar(session, pregunta_id, pregunta_update)
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return pregunta


@app.delete("/preguntas/{pregunta_id}", tags=["Preguntas"])
def eliminar_pregunta(pregunta_id: int, session: Session = Depends(get_session)):
    eliminado = PreguntaRepository.eliminar(session, pregunta_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return {"message": "Pregunta eliminada correctamente"}


# ============================================================
# EVALUACIONES
# ============================================================
@app.post("/evaluaciones", response_model=EvaluacionResponse, tags=["Evaluaciones"])
def crear_evaluacion(evaluacion: EvaluacionCreate, session: Session = Depends(get_session)):
    return EvaluacionRepository.crear(session, evaluacion)


@app.get("/evaluaciones", response_model=List[EvaluacionResponse], tags=["Evaluaciones"])
def listar_evaluaciones(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return EvaluacionRepository.listar(session, offset=offset, limit=limit)


@app.get("/evaluaciones/{evaluacion_id}", response_model=EvaluacionResponse, tags=["Evaluaciones"])
def buscar_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    evaluacion = EvaluacionRepository.buscar(session, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return evaluacion


@app.put("/evaluaciones/{evaluacion_id}", response_model=EvaluacionResponse, tags=["Evaluaciones"])
def actualizar_evaluacion(evaluacion_id: int, evaluacion_update: EvaluacionUpdate, session: Session = Depends(get_session)):
    evaluacion = EvaluacionRepository.actualizar(session, evaluacion_id, evaluacion_update)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return evaluacion


@app.delete("/evaluaciones/{evaluacion_id}", tags=["Evaluaciones"])
def eliminar_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    eliminado = EvaluacionRepository.eliminar(session, evaluacion_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return {"message": "Evaluación eliminada correctamente"}


# ============================================================
# RESPUESTAS
# ============================================================
@app.post("/respuestas", response_model=RespuestaResponse, tags=["Respuestas"])
def crear_respuesta(respuesta: RespuestaCreate, session: Session = Depends(get_session)):
    return RespuestaRepository.crear(session, respuesta)


@app.get("/respuestas", response_model=List[RespuestaResponse], tags=["Respuestas"])
def listar_respuestas(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    return RespuestaRepository.listar(session, offset=offset, limit=limit)


@app.get("/respuestas/{respuesta_id}", response_model=RespuestaResponse, tags=["Respuestas"])
def buscar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    respuesta = RespuestaRepository.buscar(session, respuesta_id)
    if not respuesta:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return respuesta


@app.put("/respuestas/{respuesta_id}", response_model=RespuestaResponse, tags=["Respuestas"])
def actualizar_respuesta(respuesta_id: int, respuesta_update: RespuestaUpdate, session: Session = Depends(get_session)):
    respuesta = RespuestaRepository.actualizar(session, respuesta_id, respuesta_update)
    if not respuesta:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return respuesta


@app.delete("/respuestas/{respuesta_id}", tags=["Respuestas"])
def eliminar_respuesta(respuesta_id: int, session: Session = Depends(get_session)):
    eliminado = RespuestaRepository.eliminar(session, respuesta_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return {"message": "Respuesta eliminada correctamente"}


# ============================================================
# ENDPOINTS ADICIONALES ÚTILES
# ============================================================
@app.get("/fichas/{ficha_id}/aprendices", response_model=List[AprendizResponse], tags=["Fichas"])
def listar_aprendices_por_ficha(ficha_id: int, session: Session = Depends(get_session)):
    return AprendizRepository.listar_por_ficha(session, ficha_id)


@app.get("/evaluaciones/{evaluacion_id}/respuestas", response_model=List[RespuestaResponse], tags=["Evaluaciones"])
def listar_respuestas_por_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    return RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "Sistema de Evaluación de Instructores - API",
        "docs": "/docs",
        "redoc": "/redoc"
    }