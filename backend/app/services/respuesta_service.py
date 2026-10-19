from typing import List, Optional, Dict, Any
from collections import defaultdict
from sqlmodel import Session
from app.models.respuesta import Respuesta
from app.schemas.respuesta import RespuestaCreate, RespuestaUpdate
from app.repositories.respuesta_repository import RespuestaRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.pregunta_repository import PreguntaRepository
from app.repositories.instructor_repository import InstructorRepository

# Escala oficial SENA (3 opciones):
#   Siempre = 5  (máximo)
#   Algunas veces = 3
#   Nunca = 1    (mínimo)
ETIQUETA = {5: "Siempre", 3: "Algunas veces", 1: "Nunca"}
MAXIMO = 5


def _mensaje_mejora(promedio: float) -> str:
    if promedio >= 4.0:
        return "Desempeño excelente (predominio de «Siempre»). Continúa así."
    if promedio >= 2.5:
        return "Desempeño regular. Reforzar los criterios con más respuestas «Algunas veces» o «Nunca»."
    return "Desempeño a mejorar (predominio de «Nunca» o «Algunas veces»). Se recomienda plan de mejora."


def _agregar_conteos(respuestas: List[Respuesta]) -> Dict[str, Any]:
    if not respuestas:
        return {
            "promedio": 0.0,
            "porcentaje": 0,
            "total_preguntas": 0,
            "escala": "Siempre / Algunas veces / Nunca",
            "maximo": MAXIMO,
            "conteos": {"Siempre": 0, "Algunas veces": 0, "Nunca": 0},
            "mensaje": "Sin respuestas",
        }
    total = sum(r.respuesta for r in respuestas)
    n = len(respuestas)
    promedio = total / n
    porcentaje = round((promedio / MAXIMO) * 100)
    conteos = {"Siempre": 0, "Algunas veces": 0, "Nunca": 0}
    for r in respuestas:
        et = ETIQUETA.get(r.respuesta)
        if et:
            conteos[et] += 1
        elif r.respuesta >= 4:
            conteos["Siempre"] += 1
        elif r.respuesta >= 2:
            conteos["Algunas veces"] += 1
        else:
            conteos["Nunca"] += 1
    return {
        "promedio": round(promedio, 2),
        "porcentaje": porcentaje,
        "total_preguntas": n,
        "escala": "Siempre / Algunas veces / Nunca",
        "maximo": MAXIMO,
        "conteos": conteos,
        "mensaje": _mensaje_mejora(promedio),
    }


class RespuestaService:
    @staticmethod
    def crear(session: Session, respuesta: RespuestaCreate) -> Respuesta:
        evaluacion = EvaluacionRepository.buscar(session, respuesta.id_evaluacion)
        if not evaluacion:
            raise ValueError("La evaluación no existe.")
        if not PreguntaRepository.buscar(session, respuesta.id_pregunta):
            raise ValueError("La pregunta no existe.")
        if not InstructorRepository.buscar(session, respuesta.id_instructor):
            raise ValueError("El instructor no existe.")
        if not (1 <= respuesta.respuesta <= 5):
            raise ValueError(
                "La calificación debe ser 1 (Nunca), 3 (Algunas veces) o 5 (Siempre)."
            )
        return RespuestaRepository.crear(session, respuesta)

    @staticmethod
    def buscar(session: Session, respuesta_id: int) -> Optional[Respuesta]:
        return RespuestaRepository.buscar(session, respuesta_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[Respuesta]:
        return RespuestaRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_evaluacion(session: Session, id_evaluacion: int) -> List[Respuesta]:
        return RespuestaRepository.listar_por_evaluacion(session, id_evaluacion)

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[Respuesta]:
        return RespuestaRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def actualizar(
        session: Session, respuesta_id: int, respuesta_update: RespuestaUpdate
    ) -> Optional[Respuesta]:
        if respuesta_update.respuesta is not None and not (
            1 <= respuesta_update.respuesta <= 5
        ):
            raise ValueError(
                "La calificación debe ser 1 (Nunca), 3 (Algunas veces) o 5 (Siempre)."
            )
        return RespuestaRepository.actualizar(session, respuesta_id, respuesta_update)

    @staticmethod
    def eliminar(session: Session, respuesta_id: int) -> bool:
        return RespuestaRepository.eliminar(session, respuesta_id)

    @staticmethod
    def calcular_puntaje(session: Session, evaluacion_id: int) -> dict:
        respuestas = RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
        return _agregar_conteos(respuestas)

    @staticmethod
    def calcular_puntaje_por_instructor(
        session: Session, evaluacion_id: int, instructor_id: int
    ) -> dict:
        respuestas = [
            r
            for r in RespuestaRepository.listar_por_evaluacion(session, evaluacion_id)
            if r.id_instructor == instructor_id
        ]
        return _agregar_conteos(respuestas)

    @staticmethod
    def consolidar_por_instructor(
        session: Session, respuestas: List[Respuesta]
    ) -> Dict[int, Dict[str, Any]]:
        por_inst: Dict[int, List[Respuesta]] = defaultdict(list)
        for r in respuestas:
            por_inst[r.id_instructor].append(r)
        return {inst_id: _agregar_conteos(rs) for inst_id, rs in por_inst.items()}
