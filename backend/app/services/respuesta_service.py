from typing import List, Optional

from sqlmodel import Session

from app.models.respuesta import Respuesta
from app.models.evaluacion import Evaluacion

from app.schemas.respuesta import (
    RespuestaCreate,
    RespuestaUpdate
)

from app.repositories.respuesta_repository import (
    RespuestaRepository
)

from app.repositories.evaluacion_repository import (
    EvaluacionRepository
)

from app.repositories.pregunta_repository import (
    PreguntaRepository
)

from app.repositories.instructor_repository import (
    InstructorRepository
)


class RespuestaService:

    @staticmethod
    def crear(
        session: Session,
        respuesta: RespuestaCreate
    ) -> Respuesta:

        evaluacion = EvaluacionRepository.buscar(
            session,
            respuesta.id_evaluacion
        )

        if not evaluacion:
            raise ValueError(
                "La evaluación no existe."
            )

        if evaluacion.estado == "Evaluado":
            raise ValueError(
                "La evaluación ya fue finalizada."
            )

        pregunta = PreguntaRepository.buscar(
            session,
            respuesta.id_pregunta
        )

        if not pregunta:
            raise ValueError(
                "La pregunta no existe."
            )

        if not pregunta.estado:
            raise ValueError(
                "La pregunta no está activa."
            )

        instructor = InstructorRepository.buscar(
            session,
            respuesta.id_instructor
        )

        if not instructor:
            raise ValueError(
                "El instructor no existe."
            )

        existente = RespuestaRepository.buscar_existente(
            session,
            respuesta.id_evaluacion,
            respuesta.id_pregunta,
            respuesta.id_instructor
        )

        if existente:
            raise ValueError(
                "Esta pregunta ya fue respondida "
                "para este instructor."
            )

        return RespuestaRepository.crear(
            session,
            respuesta
        )

    @staticmethod
    def buscar(
        session: Session,
        respuesta_id: int
    ) -> Optional[Respuesta]:

        return RespuestaRepository.buscar(
            session,
            respuesta_id
        )

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[Respuesta]:

        return RespuestaRepository.listar(
            session,
            offset,
            limit
        )

    @staticmethod
    def listar_por_evaluacion(
        session: Session,
        id_evaluacion: int
    ) -> List[Respuesta]:

        return RespuestaRepository.listar_por_evaluacion(
            session,
            id_evaluacion
        )

    @staticmethod
    def listar_por_pregunta(
        session: Session,
        id_pregunta: int
    ) -> List[Respuesta]:

        return RespuestaRepository.listar_por_pregunta(
            session,
            id_pregunta
        )

    @staticmethod
    def listar_por_instructor(
        session: Session,
        id_instructor: int
    ) -> List[Respuesta]:

        return RespuestaRepository.listar_por_instructor(
            session,
            id_instructor
        )

    @staticmethod
    def actualizar(
        session: Session,
        respuesta_id: int,
        respuesta_update: RespuestaUpdate
    ) -> Optional[Respuesta]:

        respuesta = RespuestaRepository.buscar(
            session,
            respuesta_id
        )

        if not respuesta:
            return None

        evaluacion = EvaluacionRepository.buscar(
            session,
            respuesta.id_evaluacion
        )

        if evaluacion and evaluacion.estado == "Evaluado":
            raise ValueError(
                "No se puede modificar una respuesta "
                "de una evaluación finalizada."
            )

        return RespuestaRepository.actualizar(
            session,
            respuesta_id,
            respuesta_update
        )

    @staticmethod
    def eliminar(
        session: Session,
        respuesta_id: int
    ) -> bool:

        return RespuestaRepository.eliminar(
            session,
            respuesta_id
        )

    @staticmethod
    def calcular_puntaje(
        session: Session,
        id_evaluacion: int
    ) -> float:

        respuestas = (
            RespuestaRepository.listar_por_evaluacion(
                session,
                id_evaluacion
            )
        )

        if not respuestas:
            return 0.0

        total = len(respuestas)

        positivas = sum(
            1
            for respuesta in respuestas
            if respuesta.respuesta is True
        )

        return (positivas / total) * 100

    @staticmethod
    def finalizar_evaluacion(
        session: Session,
        id_evaluacion: int
    ) -> Optional[Evaluacion]:

        evaluacion = EvaluacionRepository.buscar(
            session,
            id_evaluacion
        )

        if not evaluacion:
            return None

        if evaluacion.estado == "Evaluado":
            raise ValueError(
                "La evaluación ya fue finalizada."
            )

        respuestas = (
            RespuestaRepository.listar_por_evaluacion(
                session,
                id_evaluacion
            )
        )

        if not respuestas:
            raise ValueError(
                "No se puede finalizar una evaluación "
                "sin respuestas."
            )

        return EvaluacionRepository.actualizar_estado(
            session,
            id_evaluacion,
            "Evaluado"
        )