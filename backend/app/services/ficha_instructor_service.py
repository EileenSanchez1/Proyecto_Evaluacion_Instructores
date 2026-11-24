from typing import List, Optional
from sqlmodel import Session
from app.models.ficha_instructor import FichaInstructor
from app.schemas.ficha_instructor import FichaInstructorCreate, FichaInstructorUpdate
from app.repositories.ficha_instructor_repository import FichaInstructorRepository
from app.repositories.ficha_repository import FichaRepository
from app.repositories.instructor_repository import InstructorRepository
from app.repositories.periodo_repository import PeriodoRepository


def _valor(nuevo, actual):
    """El valor nuevo si viene en la actualización; si no, el actual."""
    return nuevo if nuevo is not None else actual


def _validar_existencia(session: Session, id_ficha: int, id_instructor: int, id_periodo: int):
    if not FichaRepository.buscar(session, id_ficha):
        raise ValueError("La ficha no existe.")
    if not InstructorRepository.buscar(session, id_instructor):
        raise ValueError("El instructor no existe.")
    if not PeriodoRepository.buscar(session, id_periodo):
        raise ValueError("El periodo no existe.")


def _validar_ra_libre(session: Session, id_ficha, id_periodo, id_resultado, relacion_id: int):
    """Un mismo RA no puede estar en dos instructores de la misma ficha+periodo."""
    if id_resultado is None:
        return
    otro_con_ra = FichaInstructorRepository.buscar_por_resultado(
        session,
        id_ficha,
        id_periodo,
        id_resultado,
        solo_activos=True,
        excluir_relacion_id=relacion_id,
    )
    if otro_con_ra is not None:
        raise ValueError(
            "Ese resultado de aprendizaje ya está asignado a otro instructor "
            "en esta ficha y periodo. Cada RA solo puede asignarse a un instructor."
        )


def _validar_sin_duplicado(session: Session, id_ficha, id_instructor, id_periodo, relacion_id):
    """Conflicto solo con OTRA asignación ACTIVA del mismo triple."""
    ex = FichaInstructorRepository.buscar_asignacion(
        session, id_ficha, id_instructor, id_periodo, solo_activos=True
    )
    if ex is not None and int(ex.id) != relacion_id:
        raise ValueError(
            "El instructor ya está asignado a esta ficha en el periodo seleccionado."
        )


def _desactivada_en_destino(session: Session, id_ficha, id_instructor, id_periodo, relacion_id):
    """Otra fila DESACTIVADA con el mismo triple (el unique también incluye desactivadas)."""
    otra = FichaInstructorRepository.buscar_asignacion_cualquier(
        session, id_ficha, id_instructor, id_periodo
    )
    if otra is None or int(otra.id) == relacion_id or getattr(otra, "activo", True):
        return None
    return otra


class FichaInstructorService:
    @staticmethod
    def crear(session: Session, ficha_instructor: FichaInstructorCreate) -> FichaInstructor:
        if not FichaRepository.buscar(session, ficha_instructor.id_ficha):
            raise ValueError("La ficha no existe.")
        if not InstructorRepository.buscar(session, ficha_instructor.id_instructor):
            raise ValueError("El instructor no existe.")
        periodo = PeriodoRepository.buscar(session, ficha_instructor.id_periodo)
        if not periodo:
            raise ValueError("El periodo no existe.")
        if str(getattr(periodo, "estado", "")).lower() != "activo":
            raise ValueError(
                "No se puede asignar instructor a un periodo desactivado. "
                "Activa el periodo o elige uno activo."
            )

        # Un mismo RA no puede estar asignado a dos instructores en la misma ficha+periodo
        if ficha_instructor.id_resultado is not None:
            otro_con_ra = FichaInstructorRepository.buscar_por_resultado(
                session,
                ficha_instructor.id_ficha,
                ficha_instructor.id_periodo,
                ficha_instructor.id_resultado,
                solo_activos=True,
            )
            if otro_con_ra is not None:
                raise ValueError(
                    "Ese resultado de aprendizaje ya está asignado a otro instructor "
                    "en esta ficha y periodo. Cada RA solo puede asignarse a un instructor."
                )

        # Si ya existe (aunque desactivada) → reactivar y actualizar RA
        existente = FichaInstructorRepository.buscar_asignacion_cualquier(
            session,
            ficha_instructor.id_ficha,
            ficha_instructor.id_instructor,
            ficha_instructor.id_periodo,
        )
        if existente:
            if getattr(existente, "activo", True):
                raise ValueError(
                    "El instructor ya está asignado a esta ficha en el periodo seleccionado."
                )
            # Reactivar y actualizar RA
            update = FichaInstructorUpdate(
                id_resultado=ficha_instructor.id_resultado,
                activo=True,
            )
            return FichaInstructorRepository.actualizar(session, existente.id, update)

        return FichaInstructorRepository.crear(session, ficha_instructor)

    @staticmethod
    def buscar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return FichaInstructorRepository.buscar(session, relacion_id)

    @staticmethod
    def listar(session: Session, offset: int = 0, limit: int = 100) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar(session, offset, limit)

    @staticmethod
    def listar_por_ficha(
        session: Session, id_ficha: int, solo_activos: bool = True
    ) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha(
            session, id_ficha, solo_activos=solo_activos
        )

    @staticmethod
    def listar_por_ficha_y_periodo(
        session: Session, id_ficha: int, id_periodo: int
    ) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_ficha_y_periodo(
            session, id_ficha, id_periodo, solo_activos=True
        )

    @staticmethod
    def listar_por_instructor(session: Session, id_instructor: int) -> List[FichaInstructor]:
        return FichaInstructorRepository.listar_por_instructor(session, id_instructor)

    @staticmethod
    def actualizar(
        session: Session, relacion_id: int, update: FichaInstructorUpdate
    ) -> Optional[FichaInstructor]:
        relacion_id = int(relacion_id)
        relacion = FichaInstructorRepository.buscar(session, relacion_id)
        if not relacion:
            return None

        id_ficha = _valor(update.id_ficha, relacion.id_ficha)
        id_instructor = _valor(update.id_instructor, relacion.id_instructor)
        id_periodo = _valor(update.id_periodo, relacion.id_periodo)
        id_resultado = _valor(update.id_resultado, relacion.id_resultado)

        _validar_existencia(session, id_ficha, id_instructor, id_periodo)
        _validar_ra_libre(session, id_ficha, id_periodo, id_resultado, relacion_id)
        _validar_sin_duplicado(session, id_ficha, id_instructor, id_periodo, relacion_id)

        otra = _desactivada_en_destino(session, id_ficha, id_instructor, id_periodo, relacion_id)
        if otra is None:
            return FichaInstructorRepository.actualizar(session, relacion_id, update)

        # Hay una desactivada en el destino: se reactiva con el RA nuevo y se desactiva la actual
        FichaInstructorRepository.actualizar(
            session,
            otra.id,
            FichaInstructorUpdate(id_resultado=id_resultado, activo=True),
        )
        FichaInstructorRepository.desactivar(session, relacion_id)
        return FichaInstructorRepository.buscar(session, otra.id)

    @staticmethod
    def desactivar(session: Session, relacion_id: int) -> bool:
        return FichaInstructorRepository.desactivar(session, int(relacion_id))

    @staticmethod
    def reactivar(session: Session, relacion_id: int) -> Optional[FichaInstructor]:
        return FichaInstructorRepository.reactivar(session, int(relacion_id))

    @staticmethod
    def eliminar(session: Session, relacion_id: int) -> bool:
        # Soft-delete por defecto
        return FichaInstructorRepository.desactivar(session, int(relacion_id))
