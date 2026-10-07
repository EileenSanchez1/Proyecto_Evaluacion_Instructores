from typing import List, Optional
from sqlmodel import Session

from app.models.resultado_aprendizaje import ResultadoAprendizaje
from app.schemas.resultado_aprendizaje import (
    ResultadoAprendizajeCreate,
    ResultadoAprendizajeUpdate,
)
from app.repositories.resultado_aprendizaje_repository import (
    ResultadoAprendizajeRepository,
)


class ResultadoAprendizajeService:

    @staticmethod
    def crear(
        session: Session,
        data: ResultadoAprendizajeCreate
    ) -> ResultadoAprendizaje:
        existente = ResultadoAprendizajeRepository.buscar_por_nombre(
            session, data.nombre
        )
        if existente:
            raise ValueError(
                "Ya existe un resultado de aprendizaje con ese nombre."
            )
        if data.codigo:
            por_codigo = ResultadoAprendizajeRepository.buscar_por_codigo(
                session, data.codigo
            )
            if por_codigo:
                raise ValueError(
                    "Ya existe un resultado de aprendizaje con ese código."
                )
        return ResultadoAprendizajeRepository.crear(session, data)

    @staticmethod
    def listar(
        session: Session,
        offset: int = 0,
        limit: int = 100
    ) -> List[ResultadoAprendizaje]:
        return ResultadoAprendizajeRepository.listar(session, offset, limit)

    @staticmethod
    def buscar(
        session: Session,
        id_resultado: int
    ) -> Optional[ResultadoAprendizaje]:
        return ResultadoAprendizajeRepository.buscar(session, id_resultado)

    @staticmethod
    def actualizar(
        session: Session,
        id_resultado: int,
        data: ResultadoAprendizajeUpdate
    ) -> Optional[ResultadoAprendizaje]:
        ra = ResultadoAprendizajeRepository.buscar(session, id_resultado)
        if not ra:
            return None
        if data.nombre:
            existente = ResultadoAprendizajeRepository.buscar_por_nombre(
                session, data.nombre
            )
            if existente and existente.id_resultado != id_resultado:
                raise ValueError(
                    "Ya existe otro resultado de aprendizaje con ese nombre."
                )
        if data.codigo:
            por_codigo = ResultadoAprendizajeRepository.buscar_por_codigo(
                session, data.codigo
            )
            if por_codigo and por_codigo.id_resultado != id_resultado:
                raise ValueError(
                    "Ya existe otro resultado de aprendizaje con ese código."
                )
        return ResultadoAprendizajeRepository.actualizar(
            session, id_resultado, data
        )

    @staticmethod
    def eliminar(session: Session, id_resultado: int) -> bool:
        return ResultadoAprendizajeRepository.eliminar(session, id_resultado)

    @staticmethod
    def reactivar(session: Session, id_resultado: int) -> bool:
        return ResultadoAprendizajeRepository.reactivar(session, id_resultado)
